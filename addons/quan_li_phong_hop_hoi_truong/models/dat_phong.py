from odoo import models, fields, api

class DatPhong(models.Model):
    _name = "dat_phong"
    _description = "Đăng ký mượn phòng"

    phong_id = fields.Many2one("quan_ly_phong_hop", string="Phòng mượn", required=True)
    nguoi_muon_id = fields.Many2one("nhan_vien", string="Người mượn", required=True)
    thoi_gian_muon_du_kien = fields.Datetime(string="Thời gian mượn dự kiến")
    thoi_gian_muon_thuc_te = fields.Datetime(string="Thời gian mượn thực tế")
    thoi_gian_tra_du_kien = fields.Datetime(string="Thời gian trả dự kiến")
    thoi_gian_tra_thuc_te = fields.Datetime(string="Thời gian trả thực tế")
    trang_thai = fields.Selection([
        ("chờ_duyệt", "Chờ duyệt"),
        ("đã_duyệt", "Đã duyệt"),
        ("đã_hủy", "Đã hủy"),
        ("đã_trả", "Đã trả")
    ], string="Trạng thái", default="chờ_duyệt")

    lich_su_ids = fields.One2many("lich_su_muon_tra", "dat_phong_id", string="Lịch sử mượn trả")

    @api.model
    def create(self, vals):
        record = super(DatPhong, self).create(vals)
        self.env["lich_su_muon_tra"].create({
            "dat_phong_id": record.id,
            "thoi_gian_muon_du_kien": record.thoi_gian_muon_du_kien,
            "thoi_gian_muon_thuc_te": record.thoi_gian_muon_thuc_te,
            "thoi_gian_tra_du_kien": record.thoi_gian_tra_du_kien,
            "thoi_gian_tra_thuc_te": record.thoi_gian_tra_thuc_te,
            "trang_thai": record.trang_thai
        })
        return record

    def write(self, vals):
        res = super(DatPhong, self).write(vals)
        for record in self:
            self.env["lich_su_muon_tra"].create({
                "dat_phong_id": record.id,
                "thoi_gian_muon_du_kien": record.thoi_gian_muon_du_kien,
                "thoi_gian_muon_thuc_te": record.thoi_gian_muon_thuc_te,
                "thoi_gian_tra_du_kien": record.thoi_gian_tra_du_kien,
                "thoi_gian_tra_thuc_te": record.thoi_gian_tra_thuc_te,
                "trang_thai": record.trang_thai
            })
        return res
    @api.onchange("trang_thai")
    def _onchange_trang_thai(self):
        for record in self:
            if record.phong_id:
                record.phong_id._compute_trang_thai()