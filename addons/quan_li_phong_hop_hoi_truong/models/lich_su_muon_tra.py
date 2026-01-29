from odoo import models, fields, api
from datetime import datetime, timedelta

class LichSuMuonTra(models.Model):
    _name = "lich_su_muon_tra"
    _description = "Lịch sử sử dụng phòng họp"
    _order = "ngay_su_dung desc, phong_id asc"

    ngay_su_dung = fields.Date(string="📅 Ngày", required=True, default=fields.Date.today)
    phong_id = fields.Many2one("quan_ly_phong_hop", string="🏢 Phòng", required=True)    
    tong_thoi_gian_su_dung = fields.Char(string="⏳ Tổng thời gian sử dụng", compute="_compute_tong_thoi_gian", store=True)

    # Sửa lại: Sử dụng model trung gian thay vì quan hệ sai qua phong_id
    chi_tiet_su_dung_ids = fields.One2many("chi_tiet_su_dung_phong", "lich_su_id", string="👥 Chi tiết sử dụng")

    @api.depends("chi_tiet_su_dung_ids.thoi_gian_su_dung")
    def _compute_tong_thoi_gian(self):
        """ Tính tổng thời gian sử dụng phòng theo giờ:phút:giây """
        for record in self:
            total_seconds = sum(record.chi_tiet_su_dung_ids.mapped('thoi_gian_su_dung_seconds'))
            
            # Chuyển đổi từ giây thành giờ:phút:giây
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            record.tong_thoi_gian_su_dung = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    @api.model
    def update_lich_su_muon_tra(self):
        """ 
        Cập nhật dữ liệu lịch sử mượn trả (Legacy method - giữ lại cho tương thích)
        Lưu ý: Giờ đã tự động cập nhật khi trả phòng, method này chỉ dùng để sync lại dữ liệu cũ
        """
        from datetime import timedelta
        dat_phong_records = self.env["dat_phong"].search([
            ("trang_thai", "=", "đã_trả"), 
            ("thoi_gian_tra_thuc_te", "!=", False)
        ])

        # Xóa các chi tiết cũ
        self.env["chi_tiet_su_dung_phong"].search([]).unlink()
        
        # Tạo lại từ đầu
        for record in dat_phong_records:
            if not record.thoi_gian_muon_thuc_te:
                continue
                
            ngay_muon = record.thoi_gian_muon_thuc_te.date()
            ngay_tra = record.thoi_gian_tra_thuc_te.date()

            for single_date in (ngay_muon + timedelta(days=n) for n in range((ngay_tra - ngay_muon).days + 1)):
                lich_su = self.search([
                    ("ngay_su_dung", "=", single_date),
                    ("phong_id", "=", record.phong_id.id)
                ], limit=1)
                
                if not lich_su:
                    lich_su = self.create({
                        "ngay_su_dung": single_date,
                        "phong_id": record.phong_id.id,
                    })
                
                self.env["chi_tiet_su_dung_phong"].create({
                    "lich_su_id": lich_su.id,
                    "dat_phong_id": record.id,
                })

