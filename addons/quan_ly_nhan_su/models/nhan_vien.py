from odoo import models, fields, api
from datetime import date

from odoo.exceptions import ValidationError

class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = 'ho_va_ten'
    _order = 'ten asc, tuoi desc'

    ma_dinh_danh = fields.Char("Mã định danh", required=True)

    ho_ten_dem = fields.Char("Họ tên đệm", required=True)
    ten = fields.Char("Tên", required=True)
    ho_va_ten = fields.Char("Họ và tên", compute="_compute_ho_va_ten", store=True)
    
    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    lich_su_cong_tac_ids = fields.One2many(
        "lich_su_cong_tac", 
        inverse_name="nhan_vien_id", 
        string = "Danh sách lịch sử công tác")
    tuoi = fields.Integer("Tuổi", compute="_compute_tuoi", store=True)
    anh = fields.Binary("Ảnh")
    danh_sach_chung_chi_bang_cap_ids = fields.One2many(
        "danh_sach_chung_chi_bang_cap", 
        inverse_name="nhan_vien_id", 
        string = "Danh sách chứng chỉ bằng cấp")
    so_nguoi_bang_tuoi = fields.Integer("Số người bằng tuổi",
                                        compute="so_nguoi_bang_tuoi",
                                        store=True
                                        )
    
    # Vai trò nghiệp vụ
    hr_role_ids = fields.Many2many('hr.role', 'nhan_vien_hr_role_rel',
                                    'nhan_vien_id', 'role_id',
                                    string="Vai trò nghiệp vụ")
    
    # Trạng thái làm việc
    trang_thai = fields.Selection([
        ('dang_lam_viec', 'Đang làm việc'),
        ('nghi_phep', 'Nghỉ phép dài hạn'),
        ('nghi_viec', 'Nghỉ việc / Khóa'),
    ], string="Trạng thái làm việc", default='dang_lam_viec', required=True)
    
    # Quyền đặt phòng
    duoc_dat_phong = fields.Boolean("Được phép đặt phòng", default=True)
    han_muc_gio_hop_ngay = fields.Float("Hạn mức giờ họp/ngày", default=8.0)
    han_muc_gio_hop_thang = fields.Float("Hạn mức giờ họp/tháng", default=160.0)
    duoc_dat_phong_vip = fields.Boolean("Được đặt phòng VIP", default=False)
    
    # Thống kê
    so_lan_dat_phong = fields.Integer("Số lần đặt phòng", compute="_compute_thong_ke", store=True)
    so_gio_hop = fields.Float("Tổng số giờ họp", compute="_compute_thong_ke", store=True)
    so_lan_muon_thiet_bi = fields.Integer("Số lần mượn thiết bị", compute="_compute_thong_ke", store=True)
    so_vi_pham = fields.Integer("Số vi phạm", compute="_compute_thong_ke", store=True)
    
    @api.depends("tuoi")
    def _compute_so_nguoi_bang_tuoi(self):
        for record in self:
            if record.tuoi:
                records = self.env['nhan_vien'].search(
                    [
                        ('tuoi', '=', record.tuoi),
                        ('ma_dinh_danh', '!=', record.ma_dinh_danh)
                    ]
                )
                record.so_nguoi_bang_tuoi = len(records)
    _sql_constrains = [
        ('ma_dinh_danh_unique', 'unique(ma_dinh_danh)', 'Mã định danh phải là duy nhất')
    ]

    @api.depends("ho_ten_dem", "ten")
    def _compute_ho_va_ten(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                record.ho_va_ten = record.ho_ten_dem + ' ' + record.ten
    
    
    
                
    @api.onchange("ten", "ho_ten_dem")
    def _default_ma_dinh_danh(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                chu_cai_dau = ''.join([tu[0][0] for tu in record.ho_ten_dem.lower().split()])
                record.ma_dinh_danh = record.ten.lower() + chu_cai_dau
    
    @api.depends("ngay_sinh")
    def _compute_tuoi(self):
        for record in self:
            if record.ngay_sinh:
                year_now = date.today().year
                record.tuoi = year_now - record.ngay_sinh.year

    @api.constrains('tuoi')
    def _check_tuoi(self):
        for record in self:
            if record.tuoi < 18:
                raise ValidationError("Tuổi không được bé hơn 18")
    
    @api.depends('hr_role_ids', 'trang_thai')
    def _compute_thong_ke(self):
        """Tính toán các thống kê về hoạt động của nhân viên"""
        for record in self:
            # TODO: Implement when integrating with meeting and equipment modules
            record.so_lan_dat_phong = 0
            record.so_gio_hop = 0.0
            record.so_lan_muon_thiet_bi = 0
            record.so_vi_pham = 0
    
    def kiem_tra_duoc_dat_phong(self):
        """Kiểm tra nhân viên có được phép đặt phòng không"""
        self.ensure_one()
        if self.trang_thai != 'dang_lam_viec':
            return False
        if not self.duoc_dat_phong:
            return False
        return True
    
    def kiem_tra_duoc_muon_thiet_bi(self):
        """Kiểm tra nhân viên có được phép mượn thiết bị không"""
        self.ensure_one()
        if self.trang_thai != 'dang_lam_viec':
            return False
        return True
