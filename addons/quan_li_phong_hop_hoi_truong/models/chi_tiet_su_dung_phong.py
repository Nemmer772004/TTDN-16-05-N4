from odoo import models, fields, api

class ChiTietSuDungPhong(models.Model):
    _name = "chi_tiet_su_dung_phong"
    _description = "Chi tiết sử dụng phòng họp theo ngày"
    _order = "thoi_gian_muon_thuc_te desc"

    lich_su_id = fields.Many2one("lich_su_muon_tra", string="Lịch sử", required=True, ondelete="cascade")
    dat_phong_id = fields.Many2one("dat_phong", string="Đăng ký", required=True, ondelete="cascade")
    
    # Related fields từ dat_phong
    nguoi_muon_id = fields.Many2one("nhan_vien", string="Người mượn", related="dat_phong_id.nguoi_muon_id", store=True)
    phong_id = fields.Many2one("quan_ly_phong_hop", string="Phòng", related="dat_phong_id.phong_id", store=True)
    ly_do = fields.Text(string="Lý do", related="dat_phong_id.ly_do", readonly=True)
    
    thoi_gian_muon_thuc_te = fields.Datetime(string="Thời gian mượn", related="dat_phong_id.thoi_gian_muon_thuc_te", store=True)
    thoi_gian_tra_thuc_te = fields.Datetime(string="Thời gian trả", related="dat_phong_id.thoi_gian_tra_thuc_te", store=True)
    
    # Computed fields
    thoi_gian_su_dung = fields.Char(string="Thời gian sử dụng", compute="_compute_thoi_gian_su_dung", store=True)
    thoi_gian_su_dung_seconds = fields.Float(string="Seconds", compute="_compute_thoi_gian_su_dung", store=True)

    @api.depends("thoi_gian_muon_thuc_te", "thoi_gian_tra_thuc_te")
    def _compute_thoi_gian_su_dung(self):
        """Tính thời gian sử dụng thực tế"""
        for record in self:
            if record.thoi_gian_muon_thuc_te and record.thoi_gian_tra_thuc_te:
                delta = record.thoi_gian_tra_thuc_te - record.thoi_gian_muon_thuc_te
                total_seconds = delta.total_seconds()
                record.thoi_gian_su_dung_seconds = total_seconds
                
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                record.thoi_gian_su_dung = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            else:
                record.thoi_gian_su_dung = "00:00:00"
                record.thoi_gian_su_dung_seconds = 0
