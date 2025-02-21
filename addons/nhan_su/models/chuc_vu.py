from odoo import models, fields


class ChucVu(models.Model):
    _name = 'chuc_vu'
    _description = 'Bảng chứa thông tin chức vụ'

    ma_chuc_vu = fields.Char("Mã chức vụ", required=True)
    ten_chuc_vu = fields.Char("Tên chức vụ", required=True)
    mo_ta = fields.Text("Mô tả")
    nhan_vien_ids = fields.One2many("nhan_vien", inverse_name="chuc_vu_id", string="Nhân viên nắm giữ chức vụ")
    phong_ban_id = fields.Many2one("phong_ban", string="Phòng ban")
