# Judge audit

## Lệnh đã chạy

- `python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5`
- `python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5`

## Kết quả calibration

| Tiêu chí | n | κ | Precision | Recall | Confusion matrix | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---:|---:|---:|---:|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | TP=24, FP=4, FN=6, TN=66 | Có | Dùng |
| helpful | 100 | 0.375 | 1.000 | 0.300 | TP=9, FP=0, FN=21, TN=70 | Không | Loại |

Failure rate của `tone_ok` quan sát được là 0.28; sau hiệu chỉnh Rogan–Gladen là 0.30.

Failure rate của `helpful` quan sát được là 0.09; sau hiệu chỉnh Rogan–Gladen là 0.30. Chênh lệch lớn xuất hiện vì judge helpful bỏ sót nhiều failure.

## Audit thủ công các bất đồng

| # | Case | Judge nói | Người nói | Ai đúng? | Hành động sửa rubric |
|---:|---|---|---|---|---|
| 1 | H-008 | PASS | FAIL | Người | Nêu rõ cách xưng hô “em”, “anh” và từ “nha” là quá suồng sã trong ngữ cảnh khiếu nại. |
| 2 | H-017 | PASS | FAIL | Người | Bổ sung ví dụ không đạt khi gọi khách là “bạn” và dùng “nha”. |
| 3 | H-029 | PASS | FAIL | Người | Bổ sung quy tắc không được ra lệnh cho khách như “không cần nhắn thêm”. |
| 4 | H-042 | FAIL | PASS | Người | Cho phép câu trả lời ngắn nếu vẫn đủ trạng thái, số tiền và thời gian nhận tiền; không bắt buộc phải xin lỗi. |
| 5 | H-051 | FAIL | PASS | Người | Ghi rõ từ “refund” được CS LogiX chấp nhận, không tự động xem là lỗi tone. |
| 6 | HL-015 | PASS | FAIL | Người | Helpful rubric phải đối chiếu số tiền trong reply với ledger, không chỉ đánh giá câu văn. |
| 7 | HL-016 | PASS | FAIL | Người | Câu trả lời lịch sự vẫn phải fail nếu số tiền sai. |
| 8 | HL-020 | PASS | FAIL | Người | Thêm kiểm tra chính xác số tiền trước khi đánh giá mức hữu ích. |
| 9 | HL-028 | PASS | FAIL | Người | Không để lời xin lỗi dài che khuất sai lệch nghiệp vụ. |
| 10 | HL-035 | PASS | FAIL | Người | Tách đánh giá tone khỏi factual correctness; sai tiền luôn là failure. |

## Kết luận

Judge `tone_ok` đạt κ=0.757, precision=0.857 và recall=0.800, đều cao hơn các floors nên có thể dùng trong phạm vi tiêu chí tone.

Judge `helpful` bị loại khỏi gate. Dù precision bằng 1.0, recall chỉ bằng 0.3 và có 21 false negative. Judge này thường đánh PASS cho câu trả lời lịch sự nhưng báo sai số tiền, nên không đủ an toàn để chặn regression.

Judge mới chỉ được calibration trên bộ replay công khai gồm 100 mẫu. Kết quả có thể không đại diện cho dữ liệu sản xuất hoặc cách diễn đạt mới. Cần nhãn người trên held-out set mới và audit định kỳ khi rubric hoặc phân phối dữ liệu thay đổi.