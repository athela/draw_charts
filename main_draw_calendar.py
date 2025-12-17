import os
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import calendar

cur_file_dir = os.path.dirname(os.path.abspath(__file__))
config_json_file = os.path.join(cur_file_dir, "draw_chart_config.json")
output_charts_dir = os.path.join(cur_file_dir, "output_charts")

class CalendarTracker:
    def __init__(self):
        config_data = self.get_config_data()
        self.title = config_data.get('title', '')
        self.year_month_range_list = config_data.get('year_and_month', [])
        if self.year_month_range_list:
            start_year, start_month = self.year_month_range_list[0][:2]
            end_year, end_month = self.year_month_range_list[-1][:2]
            self.output_file_name = f"{self.title}_{start_year}{start_month}_{end_year}{end_month}"
        else:
            self.output_file_name = self.title
        self.output_file_name = self.output_file_name.replace(' ', '_')

    @staticmethod
    def get_config_data():
        with open(config_json_file, 'r') as f:
            config_data = json.load(f)
        return config_data


    @staticmethod
    def get_days_in_month(year, month):
        """获取指定年月的天数"""
        return calendar.monthrange(year, month)[1]


    def create_calendar_tracker(self):
        """创建跳绳追踪年历表格"""
        # 设置图形大小（A4纸横向：297mm x 210mm，比例约1.414）
        # 使用英寸单位：A4横向约为11.7 x 8.3英寸
        fig, ax = plt.subplots(figsize=(8.3, 11.7))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        # 设置标题（左上角，调整大小和位置）
        fig.text(0.15, 0.86, self.title,
                 fontsize=16, fontweight='bold', ha='left', va='top')

        # 创建图例（右上角，调整大小）
        legend_elements = [
            mpatches.Patch(facecolor='yellow', edgecolor='black', linewidth=0.6, label='60-'),
            mpatches.Patch(facecolor='blue', edgecolor='black', linewidth=0.6, label='60+'),
            mpatches.Patch(facecolor='red', edgecolor='black', linewidth=0.6, label='70+')
        ]
        fig.legend(handles=legend_elements, loc='upper right',
                  bbox_to_anchor=(0.88, 0.84), fontsize=9,
                  frameon=True, fancybox=True, shadow=True, ncol=3)

        # 月份列表：2025年12月到2026年12月
        months = []
        for year, start_month, end_month in self.year_month_range_list:
            for month in range(start_month, end_month + 1):
                months.append((year, month))

        # 表格布局：每排17个小方格（1列月份 + 16列日期），两排一个月
        # 总共13个月（2025年12月 + 2026年1-12月），需要26行
        num_months = len(months)  # 13个月

        # 计算可用空间（留出标题和图例的空间）
        # 标题和图例大约占顶部5%的空间
        top_margin = 0.10
        bottom_margin = 0.04
        left_margin = 0.03
        right_margin = 0.03

        # 可用区域
        available_width = 1 - left_margin - right_margin
        available_height = 1 - top_margin - bottom_margin

        # 计算单元格大小，使表格合理填充A4纸
        # 10个月，每个月2行，共20行
        num_rows = num_months * 2
        # 17列：1列月份 + 16列日期
        num_cols = 17

        # 根据可用空间计算单元格大小
        # 月份列占可用宽度的15%，日期列占85%
        month_col_ratio = 0.08
        date_col_ratio = 0.92

        month_col_width = available_width * month_col_ratio
        date_col_width = available_width * date_col_ratio

        cell_width = date_col_width / 16  # 16列日期
        cell_height = available_height / num_rows  # 20行

        # 起始位置
        start_x = left_margin
        start_y = 1 - top_margin

        # 绘制每个月的表格
        for month_idx, (year, month) in enumerate(months):
            # 计算当前月份的两行位置（月份之间完全紧贴，无间距）
            # 每个月占2行，所以y位置递减2*cell_height
            y_row1 = start_y - month_idx * cell_height * 2  # 第一排的y位置
            y_row2 = y_row1 - cell_height  # 第二排的y位置（紧挨着第一排）

            # 获取该月的天数
            days_in_month = self.get_days_in_month(year, month)

            # 准备月份标签
            month_name = calendar.month_abbr[month]
            month_label = f"{month_name}\n{year}"

            # 绘制月份列（合并两行的单元格，完全无间距，使用极细边框）
            month_rect = mpatches.Rectangle(
                (start_x, y_row2),
                month_col_width,
                (y_row1 - y_row2),
                linewidth=0.5,
                edgecolor='black',
                facecolor='lightgray',
                alpha=0.2
            )
            ax.add_patch(month_rect)

            # 在月份单元格中显示月份名称（根据单元格大小调整字体）
            font_size = max(8, min(12, cell_height * 200))  # 根据单元格高度动态调整
            ax.text(start_x + month_col_width/2,
                   (y_row1 + y_row2)/2,
                   month_label,
                   fontsize=font_size, fontweight='bold',
                   ha='center', va='center')

            # 绘制日期列（16列，分布在两排，紧贴月份列，完全无间距）
            date_col_start_x = start_x + month_col_width

            day_num = 1
            # 第一排：显示前16天（或更少）
            for col in range(16):
                x_pos = date_col_start_x + col * cell_width
                y_pos = y_row1 - cell_height

                if day_num <= days_in_month:
                    # 绘制日期方格（第一排，完全无间距，使用极细边框）
                    date_rect = mpatches.Rectangle(
                        (x_pos, y_pos),
                        cell_width,
                        cell_height,
                        linewidth=0.4,
                        edgecolor='black',
                        facecolor='white'
                    )
                    ax.add_patch(date_rect)

                    # 在方格中显示日期数字（使用很淡的颜色，方便打印后用笔覆盖）
                    # 根据单元格大小动态调整字体
                    date_font_size = max(5, min(8, min(cell_width, cell_height) * 150))
                    ax.text(x_pos + cell_width/2,
                           y_pos + cell_height/2,
                           str(day_num),
                           fontsize=date_font_size, ha='center', va='center', fontweight='normal',
                           color='black', alpha=0.4)

                    day_num += 1
                else:
                    # 空白方格（如果该月天数少于16天）
                    date_rect = mpatches.Rectangle(
                        (x_pos, y_pos),
                        cell_width,
                        cell_height,
                        linewidth=0.4,
                        edgecolor='lightgray',
                        facecolor='white',
                        alpha=0.2
                    )
                    ax.add_patch(date_rect)

            # 第二排：显示剩余天数（从第17天开始）
            for col in range(16):
                x_pos = date_col_start_x + col * cell_width
                y_pos = y_row2 - cell_height

                if day_num <= days_in_month:
                    # 绘制日期方格（第二排，完全无间距，使用极细边框）
                    date_rect = mpatches.Rectangle(
                        (x_pos, y_pos),
                        cell_width,
                        cell_height,
                        linewidth=0.4,
                        edgecolor='black',
                        facecolor='white'
                    )
                    ax.add_patch(date_rect)

                    # 在方格中显示日期数字（使用很淡的颜色，方便打印后用笔覆盖）
                    # 根据单元格大小动态调整字体
                    date_font_size = max(5, min(8, min(cell_width, cell_height) * 150))
                    ax.text(x_pos + cell_width/2,
                           y_pos + cell_height/2,
                           str(day_num),
                           fontsize=date_font_size, ha='center', va='center', fontweight='normal',
                           color='black', alpha=0.4)

                    day_num += 1
                else:
                    # 空白方格（超出该月天数）
                    date_rect = mpatches.Rectangle(
                        (x_pos, y_pos),
                        cell_width,
                        cell_height,
                        linewidth=0.4,
                        edgecolor='lightgray',
                        facecolor='white',
                        alpha=0.2
                    )
                    ax.add_patch(date_rect)

        # 保存为PDF格式，更适合A4打印
        # 不使用tight_layout，避免自动调整间距
        plt.savefig(f'{output_charts_dir}/{self.output_file_name}.pdf', dpi=300, bbox_inches='tight', facecolor='white', format='pdf', pad_inches=0)
        plt.savefig(f'{output_charts_dir}/{self.output_file_name}.png', dpi=300, bbox_inches='tight', facecolor='white', pad_inches=0)
        print(f"年历表格已保存为: {self.output_file_name}.pdf 和 {self.output_file_name}.png")
        # plt.show()
        plt.close()


if __name__ == '__main__':
    calendar_obj = CalendarTracker()
    calendar_obj.create_calendar_tracker()

