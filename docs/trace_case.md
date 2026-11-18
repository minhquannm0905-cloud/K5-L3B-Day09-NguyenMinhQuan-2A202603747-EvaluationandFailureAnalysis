# Trace case: từ trace tới quyết định sai đầu tiên

## 1. Trial được phân tích

| Thuộc tính | Giá trị |
|---|---|
| Shape lỗi | `seeded_regression` |
| Claim và seed | `C-014@11` |
| Run chứa trial | `E-seeded_regression-20261118-cf4c` |
| Shape đối chứng | `fixed` |
| Run đối chứng | `E-fixed-20261118-cf4c` |
| Kết quả shape lỗi | FAIL — `proposal_mismatch` |
| Kết quả shape fixed | PASS — `ok` |
| Failure mode | FM-05 `pre_deducted`, FM-08 `misreport` |

## 2. Sự thật từ dữ liệu và ledger

Claim `C-014` liên quan tới đơn `O-515`.

Công cụ tính chính sách trả về quote đầy đủ:

- Tổng quyền lợi: 150.000 đồng.
- Điều khoản: `SHIP-LATE-03` và `DMG-04`.
- Lịch sử hoàn trước đó: 30.000 đồng.
- Số tiền đúng cần ghi thêm vào ledger: 120.000 đồng.

Agent phải chuyển **quote đầy đủ 150.000 đồng** cho host. Host chịu trách nhiệm trừ 30.000 đồng đã hoàn trước đó đúng một lần.

## 3. Trace của `seeded_regression`

| Event | Kind | Nội dung liên quan |
|---:|---|---|
| 1 | `handoff` | Tạo yêu cầu điều tra claim `C-014` |
| 2 | `investigator` | Đọc đơn `O-515` và dữ liệu có thẩm quyền |
| 3 | `quote` | Quote đầy đủ 150.000 đồng |
| 4 | `refund_history` | Đã hoàn trước đó 30.000 đồng |
| 5 | `proposal` | Agent tự giảm proposal xuống 120.000 đồng |
| 6 | `reply` | Thông báo đã hoàn 120.000 đồng |

Kết quả thực tế:

- Proposal của agent: 120.000 đồng.
- Host tiếp tục trừ lịch sử hoàn tiền 30.000 đồng.
- Ledger chỉ ghi: 90.000 đồng.
- Nhãn đúng: 120.000 đồng.
- Reply thông báo: 120.000 đồng.

## 4. Bước sai đầu tiên

Bước sai đầu tiên là **event 5 — `proposal`**.

Agent đã tự lấy quote 150.000 đồng trừ đi lịch sử hoàn 30.000 đồng và gửi proposal 120.000 đồng. Đây là lỗi FM-05 `pre_deducted`.

Hợp đồng của host yêu cầu agent gửi quote đầy đủ. Khi agent tự trừ trước, host lại trừ thêm một lần nữa, khiến ledger chỉ ghi 90.000 đồng.

Event 6 tiếp tục tạo FM-08: reply nói đã hoàn 120.000 đồng nhưng ledger thực tế chỉ có 90.000 đồng.

## 5. Đối chứng trên shape `fixed`

Với cùng `C-014@11`, shape `fixed` thực hiện:

| Event | Kind | Nội dung liên quan |
|---:|---|---|
| 1 | `handoff` | Handoff có contract và tool allowlist |
| 2 | `investigator` | Đọc đơn `O-515` |
| 3 | `quote` | Giữ nguyên quote đầy đủ 150.000 đồng |
| 4 | `reply` | Thông báo đã hoàn 120.000 đồng |

Shape `fixed` không tự trừ lịch sử hoàn tiền trước khi gọi host. Host áp dụng khoản đã hoàn 30.000 đồng đúng một lần:

- Ledger: 120.000 đồng.
- Nhãn: 120.000 đồng.
- Reply: 120.000 đồng.
- Kết quả: PASS.

## 6. Regression test và grader

Các kiểm tra trong `tests/test_lab9_graders.py` xác nhận:

- `RefundAmountCorrect` so sánh số tiền trong ledger với nhãn đúng và phát hiện 90.000 khác 120.000 đồng.
- `ReplyLedgerConsistent` phát hiện reply 120.000 đồng không khớp ledger 90.000 đồng.
- Trường hợp reply và ledger cùng 35.000 đồng được chấm PASS.
- Trường hợp reply 120.000 đồng nhưng ledger 90.000 đồng được chấm FAIL.

Evaluation thực tế xác nhận:

- `seeded_regression C-014@11`: FAIL.
- `fixed C-014@11`: PASS.
- Gate chặn `seeded_regression` tại `refund_amount_correct`, `pass_rate` và `reply_ledger_consistent`.

## 7. Điều trace chưa chứng minh

Trace này chứng minh chuỗi sự kiện gây double subtraction trong một trial cụ thể. Nó không tự chứng minh:

- Tần suất lỗi trên dữ liệu sản xuất.
- Hành vi với model thật thay cho MockLLM.
- Khả năng tổng quát hóa sang chính sách hoặc loại claim khác.
- Agent có “hiểu” quy tắc hay chỉ đi đúng nhánh đã lập trình.
- Năm seed có đủ để phát hiện ổn định mọi lỗi hiếm hay không.

Vì vậy trace phải được sử dụng cùng eval set, grader bằng code, paired bootstrap và CI gate.