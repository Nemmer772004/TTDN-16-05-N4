from odoo import models, fields, api, exceptions
from datetime import datetime

class DatPhong(models.Model):
    _name = "dat_phong"
    _description = "Đăng ký mượn phòng"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    phong_id = fields.Many2one("quan_ly_phong_hop", string="Phòng họp", required=True)
    nguoi_muon_id = fields.Many2one("nhan_vien", string="Người mượn", required=True)  
    ly_do = fields.Text(string="Lý do/Mục đích", help="Mô tả mục đích sử dụng phòng họp")
    ghi_chu = fields.Text(string="Ghi chú", help="Ghi chú thêm về yêu cầu đặc biệt")
    
    # Related fields từ phòng họp
    phong_vi_tri = fields.Char(string="Vị trí phòng", related="phong_id.vi_tri", readonly=True)
    phong_suc_chua = fields.Integer(string="Sức chứa", related="phong_id.suc_chua", readonly=True)
    phong_don_gia = fields.Float(string="Đơn giá/giờ", related="phong_id.don_gia_gio", readonly=True)
    
    # Đặt phòng định kỳ
    la_dat_dinh_ky = fields.Boolean(string="Đặt định kỳ", default=False)
    tan_suat_lap = fields.Selection([
        ('hang_ngay', 'Hàng ngày'),
        ('hang_tuan', 'Hàng tuần'),
        ('hai_tuan', 'Hai tuần một lần'),
    ], string="Tần suất lặp", help="Tần suất lặp lại cuộc họp")
    ngay_ket_thuc_dinh_ky = fields.Date(string="Đến ngày", help="Ngày kết thúc chuỗi họp định kỳ")
    dat_phong_goc_id = fields.Many2one("dat_phong", string="Đăng ký gốc", help="Đăng ký mẹ của chuỗi định kỳ")
    dat_phong_dinh_ky_ids = fields.One2many("dat_phong", "dat_phong_goc_id", string="Các lần họp định kỳ")
    
    # Thiết bị kèm theo (mượn từ Quản lý tài sản)
    thiet_bi_ids = fields.Many2many("tai_san", "dat_phong_tai_san_rel", "dat_phong_id", "tai_san_id", string="Thiết bị/Tài sản cần mượn")
    
    # Hình ảnh
    hinh_anh = fields.Binary(string="Hình ảnh", attachment=True)
    
    thoi_gian_muon_du_kien = fields.Datetime(string="Thời gian mượn dự kiến", required=True)
    thoi_gian_muon_thuc_te = fields.Datetime(string="Thời gian mượn thực tế")
    thoi_gian_tra_du_kien = fields.Datetime(string="Thời gian trả dự kiến", required=True)
    thoi_gian_tra_thuc_te = fields.Datetime(string="Thời gian trả thực tế")

    trang_thai = fields.Selection([
        ("chờ_duyệt", "Chờ duyệt"),
        ("đã_duyệt", "Đã duyệt"),
        ("đang_sử_dụng", "Đang sử dụng"),
        ("đã_hủy", "Đã hủy"),
        ("đã_trả", "Đã trả")
    ], string="Trạng thái", default="chờ_duyệt")
    
    # Đánh giá và chi phí
    danh_gia = fields.Selection([
        ('1', '⭐ Rất tệ'),
        ('2', '⭐⭐ Tệ'),
        ('3', '⭐⭐⭐ Trung bình'),
        ('4', '⭐⭐⭐⭐ Tốt'),
        ('5', '⭐⭐⭐⭐⭐ Xuất sắc'),
    ], string="Đánh giá", help="Đánh giá sau khi sử dụng phòng")
    nhan_xet = fields.Text(string="Nhận xét")
    
    chi_phi = fields.Float(string="Chi phí (VNĐ)", compute="_compute_chi_phi", store=True)
    thoi_gian_su_dung_gio = fields.Float(string="Thời gian sử dụng (giờ)", compute="_compute_chi_phi", store=True)

    lich_su_ids = fields.One2many("lich_su_thay_doi", "dat_phong_id", string="Lịch sử mượn trả")
    chi_tiet_su_dung_ids = fields.One2many("chi_tiet_su_dung_phong", "dat_phong_id", string="Chi Tiết Sử Dụng")

    
    @api.depends("thoi_gian_muon_thuc_te", "thoi_gian_tra_thuc_te", "phong_id.don_gia_gio")
    def _compute_chi_phi(self):
        """Tính chi phí dựa trên thời gian sử dụng thực tế"""
        for record in self:
            if record.thoi_gian_muon_thuc_te and record.thoi_gian_tra_thuc_te:
                delta = record.thoi_gian_tra_thuc_te - record.thoi_gian_muon_thuc_te
                hours = delta.total_seconds() / 3600
                record.thoi_gian_su_dung_gio = hours
                record.chi_phi = hours * (record.phong_id.don_gia_gio or 0)
            else:
                record.thoi_gian_su_dung_gio = 0
                record.chi_phi = 0
    
    def xac_nhan_duyet_phong(self):
        """ Xác nhận duyệt phòng và tự động hủy các yêu cầu bị trùng thời gian (cùng phòng hoặc khác phòng) """
        for record in self:
            if record.trang_thai != "chờ_duyệt":
                raise exceptions.UserError("Chỉ có thể duyệt yêu cầu có trạng thái 'Chờ duyệt'.")
            
            # Duyệt yêu cầu hiện tại
            record.write({"trang_thai": "đã_duyệt"})
            self.lich_su(record)

            # Hủy các yêu cầu cùng phòng có thời gian trùng lặp
            cung_phong_trung_thoi_gian = [
                ('phong_id', '=', record.phong_id.id),
                ('id', '!=', record.id),
                ('trang_thai', '=', 'chờ_duyệt'),
                ('thoi_gian_muon_du_kien', '<', record.thoi_gian_tra_du_kien),
                ('thoi_gian_tra_du_kien', '>', record.thoi_gian_muon_du_kien)
            ]
            xu_li_cung_phong_trung_thoi_gian = self.search(cung_phong_trung_thoi_gian)
            for other in xu_li_cung_phong_trung_thoi_gian:
                other.write({"trang_thai": "đã_hủy"})
                self.lich_su(other)

            # Hủy các yêu cầu khác phòng nhưng của cùng một người mượn nếu bị trùng thời gian
            khac_phong_trung_thoi_gian = [
                ('nguoi_muon_id', '=', record.nguoi_muon_id.id),
                ('id', '!=', record.id),
                ('trang_thai', '=', 'chờ_duyệt'),
                ('thoi_gian_muon_du_kien', '<', record.thoi_gian_tra_du_kien),
                ('thoi_gian_tra_du_kien', '>', record.thoi_gian_muon_du_kien)
            ]
            xu_li_khac_phong_trung_thoi_gian = self.search(khac_phong_trung_thoi_gian)
            for other in xu_li_khac_phong_trung_thoi_gian:
                other.write({"trang_thai": "đã_hủy"})
                self.lich_su(other)

    def huy_muon_phong(self):
        """ Hủy đăng ký mượn phòng """
        for record in self:
            if record.trang_thai != "chờ_duyệt":
                raise exceptions.UserError("Chỉ có thể hủy yêu cầu có trạng thái 'Chờ duyệt'.")
            record.write({"trang_thai": "đã_hủy"})
            self.lich_su(record)

    def huy_da_duyet(self):
        """ Hủy yêu cầu đã duyệt """
        for record in self:
            if record.trang_thai != "đã_duyệt":
                raise exceptions.UserError("Chỉ có thể hủy yêu cầu có trạng thái 'Đã duyệt'.")
            
            record.write({"trang_thai": "đã_hủy"})
            self.lich_su(record)

    def bat_dau_su_dung(self):
        """ Bắt đầu sử dụng phòng - Cập nhật thời gian mượn thực tế """
        for record in self:
            if record.trang_thai != "đã_duyệt":
                raise exceptions.UserError("Chỉ có thể bắt đầu sử dụng phòng có trạng thái 'Đã duyệt'.")

            # Kiểm tra nếu đã có người đang sử dụng phòng này
            kiem_tra_phong = self.env["dat_phong"].search([
                ("phong_id", "=", record.phong_id.id),
                ("trang_thai", "=", "đang_sử_dụng"),
                ("id", "!=", record.id)
            ])

            if kiem_tra_phong:
                raise exceptions.UserError(f"Phòng {record.phong_id.name} hiện đang được sử dụng. Vui lòng chờ đến khi phòng trống.")

            # Nếu không có ai đang sử dụng, cho phép bắt đầu
            record.write({
                "trang_thai": "đang_sử_dụng",
                "thoi_gian_muon_thuc_te": datetime.now()
            })
            self.lich_su(record)
            
            # TỰ ĐỘNG TẠO LỊCH SỬ SỬ DỤNG CHO THIẾT BỊ
            for thiet_bi in record.thiet_bi_ids:
                # Kiểm tra xem thiết bị đã có lịch sử đang mở chưa
                lich_su_dang_mo = self.env['lich_su_su_dung_tai_san'].search([
                    ('tai_san_id', '=', thiet_bi.id),
                    ('trang_thai', '=', 'dang_su_dung')
                ])
                
                # Chỉ tạo mới nếu chưa có lịch sử đang mở
                if not lich_su_dang_mo:
                    self.env['lich_su_su_dung_tai_san'].create({
                        'tai_san_id': thiet_bi.id,
                        'nguoi_su_dung_id': record.nguoi_muon_id.id,
                        'phong_ban_id': record.nguoi_muon_id.lich_su_cong_tac_ids[0].don_vi_id.id if record.nguoi_muon_id.lich_su_cong_tac_ids else False,
                        'ngay_bat_dau': fields.Date.today(),
                        'trang_thai': 'dang_su_dung',
                        'ly_do': f"Sử dụng trong phòng {record.phong_id.name}",
                    })
                    # Cập nhật vị trí tài sản
                    thiet_bi.write({'vi_tri': 'dang_su_dung'})


    def tra_phong(self):
        """ Trả phòng - Cập nhật thời gian trả thực tế và tự động cập nhật lịch sử """
        for record in self:
            if record.trang_thai != "đang_sử_dụng":
                raise exceptions.UserError("Chỉ có thể trả phòng đang ở trạng thái 'Đang sử dụng'.")
            current_time = datetime.now()
            record.write({
                "trang_thai": "đã_trả",
                "thoi_gian_tra_thuc_te": current_time,
                "thoi_gian_muon_thuc_te": record.thoi_gian_muon_thuc_te or current_time
            })
            self.lich_su(record)
            
            # TỰ ĐỘNG ĐÓNG LỊCH SỬ SỬ DỤNG THIẾT BỊ
            for thiet_bi in record.thiet_bi_ids:
                # Tìm lịch sử đang mở của thiết bị
                lich_su_dang_mo = self.env['lich_su_su_dung_tai_san'].search([
                    ('tai_san_id', '=', thiet_bi.id),
                    ('nguoi_su_dung_id', '=', record.nguoi_muon_id.id),
                    ('trang_thai', '=', 'dang_su_dung')
                ])
                
                # Đóng lịch sử
                for lich_su in lich_su_dang_mo:
                    lich_su.write({
                        'trang_thai': 'da_tra',
                        'ngay_ket_thuc': fields.Date.today(),
                    })
                
                # Cập nhật vị trí tài sản về kho
                thiet_bi.write({'vi_tri': 'kho'})
            
            # Tự động cập nhật lịch sử mượn trả
            self._update_lich_su_muon_tra_auto(record)

    @api.model
    def lich_su(self, record):
        """ Ghi vào lịch sử mượn trả """
        self.env["lich_su_thay_doi"].create({
            "dat_phong_id": record.id,
            "nguoi_muon_id": record.nguoi_muon_id.id,
            "thoi_gian_muon_du_kien": record.thoi_gian_muon_du_kien,
            "thoi_gian_muon_thuc_te": record.thoi_gian_muon_thuc_te,
            "thoi_gian_tra_du_kien": record.thoi_gian_tra_du_kien,
            "thoi_gian_tra_thuc_te": record.thoi_gian_tra_thuc_te,
            "trang_thai": record.trang_thai
        })

    def _update_lich_su_muon_tra_auto(self, record):
        """Tự động cập nhật lịch sử mượn trả khi trả phòng"""
        from datetime import timedelta
        
        if not record.thoi_gian_muon_thuc_te or not record.thoi_gian_tra_thuc_te:
            return
            
        ngay_muon = record.thoi_gian_muon_thuc_te.date()
        ngay_tra = record.thoi_gian_tra_thuc_te.date()
        
        # Tạo hoặc tìm lịch sử cho từng ngày trong khoảng thời gian sử dụng
        for single_date in (ngay_muon + timedelta(days=n) for n in range((ngay_tra - ngay_muon).days + 1)):
            # Tìm hoặc tạo bản ghi lịch sử
            lich_su = self.env["lich_su_muon_tra"].search([
                ("ngay_su_dung", "=", single_date),
                ("phong_id", "=", record.phong_id.id)
            ], limit=1)
            
            if not lich_su:
                lich_su = self.env["lich_su_muon_tra"].create({
                    "ngay_su_dung": single_date,
                    "phong_id": record.phong_id.id,
                })
            
            # Tạo chi tiết sử dụng
            existing_detail = self.env["chi_tiet_su_dung_phong"].search([
                ("lich_su_id", "=", lich_su.id),
                ("dat_phong_id", "=", record.id)
            ])
            
            if not existing_detail:
                self.env["chi_tiet_su_dung_phong"].create({
                    "lich_su_id": lich_su.id,
                    "dat_phong_id": record.id,
                })

    @api.model
    def create(self, vals):
        """Override create để xử lý đặt phòng định kỳ"""
        record = super(DatPhong, self).create(vals)
        
        # Nếu là đặt phòng định kỳ, tạo các đăng ký con
        if record.la_dat_dinh_ky and record.tan_suat_lap and record.ngay_ket_thuc_dinh_ky:
            record._tao_dat_phong_dinh_ky()
        
        return record
    
    def _tao_dat_phong_dinh_ky(self):
        """Tạo các đăng ký mượn phòng định kỳ"""
        self.ensure_one()
        from datetime import timedelta
        
        if not self.la_dat_dinh_ky or not self.tan_suat_lap or not self.ngay_ket_thuc_dinh_ky:
            return
        
        # Xác định khoảng cách giữa các lần
        delta_map = {
            'hang_ngay': 1,
            'hang_tuan': 7,
            'hai_tuan': 14,
        }
        delta_days = delta_map.get(self.tan_suat_lap, 7)
        
        # Tính thời gian của một lượt họp
        thoi_luong = self.thoi_gian_tra_du_kien - self.thoi_gian_muon_du_kien
        
        current_date = self.thoi_gian_muon_du_kien.date() + timedelta(days=delta_days)
        end_date = self.ngay_ket_thuc_dinh_ky
        
        created_records = []
        while current_date <= end_date:
            # Tạo datetime cho lần họp này
            new_muon = datetime.combine(current_date, self.thoi_gian_muon_du_kien.time())
            new_tra = new_muon + thoi_luong
            
            # Kiểm tra xem có trùng không
            trung_lap = self.search([
                ('phong_id', '=', self.phong_id.id),
                ('trang_thai', 'in', ['chờ_duyệt', 'đã_duyệt', 'đang_sử_dụng']),
                ('thoi_gian_muon_du_kien', '<', new_tra),
                ('thoi_gian_tra_du_kien', '>', new_muon)
            ])
            
            if not trung_lap:
                # Tạo đăng ký mới
                new_record = self.create({
                    'phong_id': self.phong_id.id,
                    'nguoi_muon_id': self.nguoi_muon_id.id,
                    'ly_do': self.ly_do,
                    'thoi_gian_muon_du_kien': new_muon,
                    'thoi_gian_tra_du_kien': new_tra,
                    'la_dat_dinh_ky': False,  # Không tạo định kỳ cho đăng ký con
                    'dat_phong_goc_id': self.id,
                })
                created_records.append(new_record.id)
            
            current_date += timedelta(days=delta_days)
        
        if created_records:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Thành công',
                    'message': f'Đã tạo {len(created_records)} đăng ký định kỳ',
                    'type': 'success',
                    'sticky': False,
                }
            }
