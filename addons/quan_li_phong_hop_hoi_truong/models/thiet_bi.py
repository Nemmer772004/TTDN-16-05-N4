from odoo import models, fields, api

class ThietBi(models.Model):
    _name = "thiet_bi"
    _description = "Quản lý thiết bị phòng họp"
    _order = "phong_id asc, trang_thai asc"

    name = fields.Char(string="Tên thiết bị", required=True)
    loai_thiet_bi = fields.Selection([
        ('may_chieu', 'Máy chiếu'),
        ('micro', 'Micro'),
        ('loa', 'Loa'),
        ('dieu_hoa', 'Điều hòa'),
        ('may_tinh', 'Máy tính'),
        ('khac', 'Khác'),
    ], string="Loại thiết bị", required=True)
    
    phong_id = fields.Many2one("quan_ly_phong_hop", string="Phòng họp", required=True)
    trang_thai = fields.Selection([
        ('dang_su_dung', 'Đang sử dụng'),
        ('san_sang', 'Sẵn sàng'),
        ('can_bao_tri', 'Cần bảo trì'),
        ('hong', 'Hỏng'),
    ], string="Trạng thái", default="san_sang")

    mo_ta = fields.Text(string="Mô tả")
    
    

    @api.model
    def bao_tri_thiet_bi(self):
        """ Chuyển thiết bị có trạng thái 'Cần bảo trì' thành 'Sẵn sàng' sau khi bảo trì """
        thiet_bi_bao_tri = self.search([('trang_thai', '=', 'can_bao_tri')])
        thiet_bi_bao_tri.write({'trang_thai': 'san_sang'})
