from pyecharts.charts import Bar, Line
import pyecharts.options as opts
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot


class MainSrChart:
    x_data = []
    finished = []
    receive = []
    unfinished = []

    def __init__(self, month_sr):
        for sr in month_sr:
            self.x_data.append(sr['month'])
            self.finished.append(sr['finished'])
            self.receive.append(sr['receive'])
            self.unfinished.append(sr['unfinished'])

    def make_chart(self):
        bar = (
            Bar(init_opts=opts.InitOpts(width="1600px", height="500px"))
                .add_xaxis(xaxis_data=self.x_data)
                .add_yaxis(
                series_name="累计未完成",
                y_axis=self.unfinished,
                bar_width=40,
                label_opts=opts.LabelOpts(is_show=True),
            )
                .set_global_opts(
                tooltip_opts=opts.TooltipOpts(
                    is_show=True, trigger="axis", axis_pointer_type="cross"
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="shadow"),
                )
            )
        )

        line = (
            Line()
                .add_xaxis(xaxis_data=self.x_data)
                .add_yaxis(
                z_level=1,
                series_name="每月处理完成",
                y_axis=self.finished,
                label_opts=opts.LabelOpts(is_show=True),
                linestyle_opts=opts.LineStyleOpts(color="blue", width=4, type_="solid"),
                itemstyle_opts=opts.ItemStyleOpts(
                    border_width=3, border_color="blue", color="blue"
                ),
            ).add_yaxis(
                z_level=1,
                series_name="每月新收到",
                y_axis=self.receive,
                label_opts=opts.LabelOpts(is_show=True),
                linestyle_opts=opts.LineStyleOpts(color="green", width=4, type_="solid"),
                itemstyle_opts=opts.ItemStyleOpts(
                    border_width=3, border_color="green", color="green"
                ),
            )
        )
        make_snapshot(snapshot, bar.overlap(line).render("report.html"), "bar.png")
