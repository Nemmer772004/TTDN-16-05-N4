from odoo import models, fields, api

class BaoCaoSuDungPhong(models.Model):
    _name = "bao_cao_su_dung_phong"
    _description = "Báo cáo sử dụng phòng họp"
    _auto = False
    _order = "ngay desc"

    ngay = fields.Date(string="Ngày", readonly=True)
    phong_id = fields.Many2one("quan_ly_phong_hop", string="Phòng họp", readonly=True)
    nguoi_muon_id = fields.Many2one("nhan_vien", string="Người mượn", readonly=True)
    
    so_lan_su_dung = fields.Integer(string="Số lần sử dụng", readonly=True)
    tong_thoi_gian_gio = fields.Float(string="Tổng giờ sử dụng", readonly=True)
    tong_chi_phi = fields.Float(string="Tổng chi phí", readonly=True)
    
    trung_binh_danh_gia = fields.Float(string="Đánh giá TB", readonly=True)
    
    def init(self):
        """Tạo SQL view cho báo cáo"""
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
                    AVG(CAST(dp.danh_gia AS FLOAT)) AS trung_binh_danh_gia
                FROM dat_phong dp
                LEFT JOIN quan_ly_phong_hop ph ON dp.phong_id = ph.id
                WHERE dp.trang_thai = 'đã_trả'
                    AND dp.thoi_gian_muon_thuc_te IS NOT NULL
                    AND dp.thoi_gian_tra_thuc_te IS NOT NULL
                GROUP BY DATE(dp.thoi_gian_muon_thuc_te), dp.phong_id, dp.nguoi_muon_id
            )
        """)
