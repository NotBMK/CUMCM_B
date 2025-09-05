import matplotlib.pyplot as plt

from .calc import ndarray, Result
from .args import Namespace

plt.rcParams['font.sans-serif'] = ["SimHei"]
plt.rcParams['axes.unicode_minus'] = False

class Ploter(list[Result]):
    def plot(self, params: Namespace):
        for result in self:
            plt.figure(figsize=params.figure_size)

            plt.plot(result.wavecount, result.reflectence, 'b-', linewidth=params.line_width, label="反射率谱")
            if len(result.max_wavecount) > 0:
                plt.plot(result.max_wavecount, result.max_reflectence, 'ro', markersize=params.max_marker_size,
                         label=f"极大值 {len(result.max_wavecount)} 个", zorder=5)
                
                for i, (w, r) in enumerate(zip(result.max_wavecount, result.max_reflectence)):
                    plt.annotate(f"Max{i+1}\n{w:.1f}",xy=(w, r), xytext=(5, 10),
                                 textcoords="offset points",
                                 fontsize=params.annotation_size,
                                 ha="center", color="red",
                                 bbox={
                                     'boxstyle': 'round,pad=0.3',
                                     'facecolor': 'white',
                                     'alpha': 0.7
                                 })
                    
            if len(result.min_wavecount) > 0:
                plt.plot(result.min_wavecount, result.min_reflectence, 'ro', markersize=params.max_marker_size,
                         label=f"极大值 {len(result.min_wavecount)} 个", zorder=5)
                
                for i, (w, r) in enumerate(zip(result.min_wavecount, result.min_reflectence)):
                    plt.annotate(f"Min{i+1}\n{w:.1f}",xy=(w, r), xytext=(5, 10),
                                 textcoords="offset points",
                                 fontsize=params.annotation_size,
                                 ha="center", color="red",
                                 bbox={
                                     'boxstyle': 'round,pad=0.3',
                                     'facecolor': 'white',
                                     'alpha': 0.7
                                 })
                    
            plt.axvline(x=params.min_wavecount, color="grey", linestyle="--", alpha=0.5, label="检测范围")
            plt.axvline(x=params.max_wavecount, color="grey", linestyle="--", alpha=0.5)

            plt.xlabel("波数 (cm-1)", fontsize=params.font_size)
            plt.ylabel("反射率 (%)", fontsize=params.font_size)
            plt.title(f"{result.filepath} - 入射角 {result.incident_angle} °", fontsize=params.title_size)
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
        plt.show()