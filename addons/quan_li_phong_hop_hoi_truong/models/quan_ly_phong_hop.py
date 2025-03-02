from odoo import models, fields

class QuanLyPhongHop(models.Model):
    _name = "quan_ly_phong_hop"
    _description = "Quản lý phòng họp, hội trường"

    name = fields.Char(string='Tên phòng họp', required=True)
    loai_phong = fields.Selection([
        ('Phòng họp', 'Phòng họp'),
        ('Hội trường', 'Hội trường'),
    ], string='Loại phòng', required=True, default='Phòng họp')
    suc_chua = fields.Integer(string='Sức chứa')
    trang_thai = fields.Selection([
        ('Có sẵn', 'Có sẵn'),
        ('Đã mượn', 'Đã mượn'),
    ], string='Trạng thái', required=True, default='Có sẵn')

    
    