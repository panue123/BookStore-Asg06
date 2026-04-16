"""
Demo seed: tạo reviews/ratings cho các sản phẩm.
book_id ở đây tương ứng với product_id trong product-service.

Usage (trong container):
  python manage.py shell -c "from app.seeds import run; run()"
"""
from app.models import Comment

# product_id → list of (customer_id, rating, content)
REVIEWS = {
    1: [  # Clean Code
        (1, 5, "Cuốn sách tuyệt vời, thay đổi cách tôi viết code hoàn toàn. Rất khuyến khích cho mọi lập trình viên."),
        (2, 5, "Đây là cuốn sách bắt buộc phải đọc. Tác giả giải thích rất rõ ràng và có nhiều ví dụ thực tế."),
        (3, 4, "Nội dung hay, nhưng một số phần hơi khó hiểu với người mới. Cần đọc lại nhiều lần."),
        (4, 5, "Mua lần 2 vì cuốn đầu bị mất. Sách quá hay, xứng đáng 5 sao."),
    ],
    2: [  # Design Patterns
        (1, 4, "Kinh điển về design patterns. Khó đọc nhưng rất bổ ích cho career dài hạn."),
        (5, 5, "Gang of Four là must-read. Giải thích 23 patterns rất chi tiết với UML diagram."),
        (6, 3, "Sách hay nhưng hơi cũ, một số patterns không còn phù hợp với modern development."),
    ],
    3: [  # Lược sử thời gian
        (2, 5, "Hawking viết rất dễ hiểu dù chủ đề phức tạp. Đọc xong thấy vũ trụ thật kỳ diệu."),
        (7, 5, "Cuốn sách khoa học hay nhất tôi từng đọc. Mở ra nhiều góc nhìn mới về vũ trụ."),
        (8, 4, "Nội dung sâu sắc, cần đọc chậm để hiểu. Dịch thuật tốt."),
    ],
    4: [  # Sapiens
        (3, 5, "Harari viết rất cuốn hút. Nhìn lại lịch sử loài người từ góc độ hoàn toàn mới."),
        (9, 5, "Đây là cuốn sách thay đổi tư duy của tôi. Highly recommended!"),
        (10, 4, "Rất thú vị nhưng một số luận điểm còn tranh cãi. Đọc với tư duy phản biện."),
        (1, 5, "Mua tặng bạn bè nhiều lần. Ai đọc cũng thích."),
    ],
    5: [  # Tôi thấy hoa vàng
        (4, 5, "Nguyễn Nhật Ánh viết quá hay. Đọc mà nhớ lại tuổi thơ, vừa cười vừa khóc."),
        (11, 5, "Cuốn sách tuổi thơ không thể thiếu. Văn phong trong sáng, cảm xúc chân thật."),
        (12, 4, "Hay nhưng hơi buồn. Đọc xong thấy trân trọng tuổi thơ hơn."),
    ],
    6: [  # Khởi nghiệp tinh gọn
        (5, 5, "Lean Startup là bible cho startup. Áp dụng được ngay vào thực tế."),
        (13, 4, "Nhiều case study thực tế. Phương pháp MVP rất hữu ích."),
        (14, 5, "Đọc xong thay đổi hoàn toàn cách tiếp cận sản phẩm. Rất recommend."),
    ],
    7: [  # Đắc nhân tâm
        (6, 5, "Classic không bao giờ lỗi thời. Đọc đi đọc lại vẫn học được điều mới."),
        (15, 5, "Cuốn sách kỹ năng mềm hay nhất. Thay đổi cách tôi giao tiếp với mọi người."),
        (16, 4, "Hay nhưng một số ví dụ hơi cũ. Nguyên tắc vẫn đúng đến ngày nay."),
        (2, 5, "Mua tặng cả team. Ai cũng thích."),
    ],
    8: [  # Hoàng tử bé
        (7, 5, "Không chỉ là sách thiếu nhi. Người lớn đọc càng thấm hơn."),
        (17, 5, "Triết lý sâu sắc ẩn trong câu chuyện đơn giản. Đọc mãi không chán."),
        (18, 4, "Bản dịch đẹp, hình minh họa đáng yêu. Mua tặng con rất phù hợp."),
    ],
    9: [  # Samsung Galaxy S24 Ultra
        (8, 5, "Camera 200MP chụp ảnh cực đẹp. S Pen rất tiện cho ghi chú. Đáng tiền."),
        (19, 4, "Máy mạnh, pin tốt. Hơi nặng nhưng chấp nhận được với màn hình lớn."),
        (20, 5, "Flagship tốt nhất Android hiện tại. Zoom 100x ảo diệu."),
    ],
    10: [  # Dell XPS 15
        (9, 5, "Màn hình OLED đẹp xuất sắc. Hiệu năng mạnh, phù hợp cho developer."),
        (21, 4, "Laptop tốt nhưng pin hơi yếu khi dùng nặng. Build quality premium."),
        (22, 5, "Mua để code và design. Không thất vọng. Đáng đầu tư."),
    ],
    11: [  # iPhone 15 Pro Max
        (10, 5, "Camera Action Button rất tiện. Chip A17 Pro siêu nhanh. iOS mượt mà."),
        (23, 4, "Đẹp, mạnh nhưng giá cao. Titanium frame sang trọng hơn hẳn."),
        (24, 5, "Upgrade từ iPhone 13, khác biệt rõ rệt. Rất hài lòng."),
    ],
    13: [  # Nike Air Max 270
        (11, 5, "Đệm khí êm ái, đi cả ngày không mỏi chân. Thiết kế đẹp."),
        (25, 4, "Size chuẩn, chất lượng tốt. Giá hơi cao nhưng xứng đáng."),
        (26, 5, "Mua lần 2, lần trước đi 2 năm mới hỏng. Chất lượng Nike không phải bàn."),
    ],
    14: [  # L'Oréal Revitalift Serum
        (12, 5, "Dùng 2 tuần thấy da căng mịn hơn rõ rệt. Mùi dễ chịu, thấm nhanh."),
        (27, 4, "Hiệu quả tốt nhưng giá hơi cao. Sẽ mua lại."),
        (28, 5, "Da khô dùng rất phù hợp. Hyaluronic Acid cấp ẩm tốt."),
    ],
    17: [  # LEGO Technic Bugatti
        (13, 5, "Mua tặng con trai 16 tuổi. Lắp mất 3 ngày, đẹp không tưởng. Đáng tiền."),
        (29, 5, "Collector item. Chi tiết cực kỳ tỉ mỉ. Xứng đáng là flagship của LEGO."),
        (30, 4, "Khó lắp nhưng thành phẩm rất đẹp. Cần kiên nhẫn."),
    ],
    21: [  # Sữa Vinamilk Organic
        (14, 5, "Sữa ngon, thơm tự nhiên. Con tôi rất thích. Mua thường xuyên."),
        (31, 4, "Chất lượng tốt, giá hợp lý. Organic nên yên tâm hơn."),
        (32, 5, "Mua cả thùng mỗi tháng. Gia đình dùng đều thích."),
    ],
}


def run():
    created = 0
    skipped = 0
    for product_id, reviews in REVIEWS.items():
        for customer_id, rating, content in reviews:
            _, is_new = Comment.objects.get_or_create(
                customer_id=customer_id,
                book_id=product_id,   # book_id field = product_id (backward compat)
                defaults={"content": content, "rating": rating},
            )
            if is_new:
                created += 1
            else:
                skipped += 1
    print(f"Reviews seeded: {created} new, {skipped} already existed")
    return created
