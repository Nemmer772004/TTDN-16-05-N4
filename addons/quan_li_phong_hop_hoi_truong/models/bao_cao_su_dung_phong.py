from odoo import models, fields, api

class BaoCaoSuDungPhong(models.Model):
    _name = "bao_cao_su_dung_phong"
    _description = "Báo cáo sử dụng phòng họp"
    _auto = False
    _order = "ngay desc, phong_id"

    ngay = fields.Date(string="Ngày", readonly=True)
    phong_id = fields.Many2one("quan_ly_phong_hop", string="Phòng họp", readonly=True)
    nguoi_muon_id = fields.Many2one("nhan_vien", string="Người mượn", readonly=True)
    
    so_lan_su_dung = fields.Integer(string="Số lần sử dụng", readonly=True, group_operator="sum")
    tong_thoi_gian_gio = fields.Float(string="Tổng giờ sử dụng (h)", readonly=True, group_operator="sum")
    tong_chi_phi = fields.Float(string="Tổng chi phí (VNĐ)", readonly=True, group_operator="sum")
    
    trung_binh_danh_gia = fields.Float(string="Đánh giá TB", readonly=True, group_operator="avg")
    
    # Thêm fields hỗ trợ phân tích
    thang = fields.Integer(string="Tháng", readonly=True)
    quy = fields.Integer(string="Quý", readonly=True)
    nam = fields.Integer(string="Năm", readonly=True)
    
    def init(self):
        """Tạo SQL view cho báo cáo với hỗ trợ phân tích nâng cao"""
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW bao_cao_su_dung_phong AS (
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY DATE(dp.thoi_gian_muon_thuc_te), dp.phong_id, dp.nguoi_muon_id) AS id,
                    DATE(dp.thoi_gian_muon_thuc_te) AS ngay,
                    dp.phong_id,
                    dp.nguoi_muon_id,
                    COUNT(dp.id) AS so_lan_su_dung,
                    SUM(EXTRACT(EPOCH FROM (dp.thoi_gian_tra_thuc_te - dp.thoi_gian_muon_thuc_te)) / 3600) AS tong_thoi_gian_gio,
                    SUM(EXTRACT(EPOCH FROM (dp.thoi_gian_tra_thuc_te - dp.thoi_gian_muon_thuc_te)) / 3600 * COALESCE(ph.don_gia_gio, 0)) AS tong_chi_phi,
                    AVG(CAST(dp.danh_gia AS FLOAT)) AS trung_binh_danh_gia,
                    EXTRACT(MONTH FROM dp.thoi_gian_muon_thuc_te) AS thang,
                    EXTRACT(QUARTER FROM dp.thoi_gian_muon_thuc_te) AS quy,
                    EXTRACT(YEAR FROM dp.thoi_gian_muon_thuc_te) AS nam
                FROM dat_phong dp
                LEFT JOIN quan_ly_phong_hop ph ON dp.phong_id = ph.id
                WHERE dp.trang_thai = 'đã_trả'
                    AND dp.thoi_gian_muon_thuc_te IS NOT NULL
                    AND dp.thoi_gian_tra_thuc_te IS NOT NULL
                GROUP BY DATE(dp.thoi_gian_muon_thuc_te), dp.phong_id, dp.nguoi_muon_id,
                         EXTRACT(MONTH FROM dp.thoi_gian_muon_thuc_te),
                         EXTRACT(QUARTER FROM dp.thoi_gian_muon_thuc_te),
                         EXTRACT(YEAR FROM dp.thoi_gian_muon_thuc_te)
            )
        """)
    
    @api.model
    def get_comparison_data(self, domain=None, date_from=None, date_to=None, compare_period='previous_month'):
        """
        Lấy dữ liệu so sánh giữa các khoảng thời gian
        
        Args:
            domain: Domain filter
            date_from: Ngày bắt đầu
            date_to: Ngày kết thúc  
            compare_period: 'previous_month', 'previous_quarter', 'previous_year'
        
        Returns:
            dict: {
                'current': {...},
                'previous': {...},
                'growth': {...}
            }
        """
        if not date_from or not date_to:
            return {}
        
        # Tính toán khoảng thời gian trước đó
        if compare_period == 'previous_month':
            date_from_prev = fields.Date.subtract(date_from, months=1)
            date_to_prev = fields.Date.subtract(date_to, months=1)
        elif compare_period == 'previous_quarter':
            date_from_prev = fields.Date.subtract(date_from, months=3)
            date_to_prev = fields.Date.subtract(date_to, months=3)
        elif compare_period == 'previous_year':
            date_from_prev = fields.Date.subtract(date_from, years=1)
            date_to_prev = fields.Date.subtract(date_to, years=1)
        else:
            return {}
        
        # Lấy dữ liệu kỳ hiện tại
        current_domain = [('ngay', '>=', date_from), ('ngay', '<=', date_to)]
        if domain:
            current_domain += domain
        
        current_data = self.read_group(
            current_domain,
            ['so_lan_su_dung', 'tong_thoi_gian_gio', 'tong_chi_phi', 'trung_binh_danh_gia'],
            []
        )
        
        # Lấy dữ liệu kỳ trước
        previous_domain = [('ngay', '>=', date_from_prev), ('ngay', '<=', date_to_prev)]
        if domain:
            previous_domain += domain
        
        previous_data = self.read_group(
            previous_domain,
            ['so_lan_su_dung', 'tong_thoi_gian_gio', 'tong_chi_phi', 'trung_binh_danh_gia'],
            []
        )
        
        # Tính toán tăng trưởng
        current = current_data[0] if current_data else {}
        previous = previous_data[0] if previous_data else {}
        
        growth = {}
        for field in ['so_lan_su_dung', 'tong_thoi_gian_gio', 'tong_chi_phi', 'trung_binh_danh_gia']:
            current_val = current.get(field, 0) or 0
            previous_val = previous.get(field, 0) or 0
            
            if previous_val > 0:
                growth[field] = ((current_val - previous_val) / previous_val) * 100
            else:
                growth[field] = 100 if current_val > 0 else 0
        
        return {
            'current': current,
            'previous': previous,
            'growth': growth
        }

