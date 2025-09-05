from .args import Namespace
from numpy import ndarray
from numpy import mean, sort, radians, sin, sqrt, std
from pandas import DataFrame
from pandas import read_csv, read_excel
from scipy.signal import find_peaks

def refractive_index(wavecounts: ndarray) -> ndarray:
    '''
    计算折射率
    '''
    A = 2.6161
    C = 2.823e-10
    return A + C * wavecounts ** 2

class Analyzer:
    def __init__(self, params: Namespace):
        self.params = params
        self.debug: bool = params.debug

        if self.debug:
            self.print = self._print
        else:
            self.print = self._no_print

    def _print(self, *values: object,
              sep: str | None = " ",
              end: str | None = "\n"):
        print(*values, sep=sep, end=end)

    def _no_print(self, *values: object,
        sep: str | None = " ",
        end: str | None = "\n"):
        pass
    
    def read_data(self, filepath: str) -> tuple[DataFrame|None, DataFrame|None]:
        """
        读取数据文件
        
        返回值
        ---
        波数（cm^-1）, 反射率（%）

        失败时返回 [None, None]
        """
        try:
            if filepath.endswith('xlsx') or filepath.endswith("xls"):
                data = read_excel(filepath)
            else:
                data = read_csv(filepath)

            wave = data.iloc[:, 0].values
            refl = data.iloc[:, 1].values

            self.print(f"成功读取文件 \"{filepath}\"")
            self.print(f"\t数据点数: {len(wave)}")
            self.print(f"\t波数范围 : [{wave.min():.1f}, {wave.max():.1f}] (cm^-1)")
            self.print(f"\t反射率范围: [{refl.min():.2f}, {refl.max():.2f}] (%)")

            return wave, refl
        except Exception as e:
            print(f"读取文件失败: \"{filepath}\"")
            print(f"错误信息: {e}")
            return None, None
        
    def find_ex(self, wavecount: ndarray, reflectance: ndarray):
        wave_min = self.params.min_wavecount
        wave_max = self.params.max_wavecount
        mask = (wavecount >= wave_min) & (wavecount <= wave_max)

        wave = wavecount[mask]
        refl = reflectance[mask]

        self.print(f"过滤后的数据:")
        self.print(f"\t{wave}")
        self.print(f"\t{refl}")

        if len(wave) < 10:
            print("数据点过少，无法检测极值")
            return None, None, None, None
        
        mean_refl = mean(refl)

        self.print(f"反射率均值: {mean_refl}")

        max_peaks, _ = find_peaks(
            refl,
            prominence=self.params.max_prominence,
            distance=self.params.max_distance,
            height=mean_refl + self.params.max_height_factor
        )

        min_peaks, _ = find_peaks(
            -refl,
            prominence=self.params.min_prominence,
            distance=self.params.min_distance,
            height=-(mean_refl + self.params.min_height_factor)
        )

        max_wave = wave[max_peaks]
        max_refl = refl[max_peaks]
        min_wave = wave[min_peaks]
        min_refl = refl[min_peaks]

        self.print(f"极值检测结果:  [{wave_min}, {wave_max}] (cm^-1)")
        self.print(f"\t极大值: {len(max_wave)} 个")
        self.print(f"\t极小值: {len(min_wave)} 个")

        return max_wave, max_refl, min_wave, min_refl
    
    def calculate_thickness(self, wavecount_ex, incident_angle_deg, method: str = 'max'):
        if len(wavecount_ex) < 2:
            print(f"极值点过少，无法计算")
            return [], []
        
        wavecount = sort(wavecount_ex)
        indicent_angle = radians(incident_angle_deg)
        offset = 0 if method == 'max' else 0.5

        thickness_history = []
        thickness_details = []

        for i in range(len(wavecount) - 1):
            v = wavecount[i:i+2]
            n = refractive_index(v)
            sin_theta = sin(indicent_angle) / n

            self.print(f"计算第{i+1}个点对:")

            if sin_theta[0] > 1 or sin_theta[1] > 1:
                self.print(f"\t点对 {v} 发生全反射，跳过")
                continue

            cos_theta = sqrt(1 - sin_theta**2)

            term = n * v * cos_theta

            numerator = (1 + offset) * term[0] - offset * term[1]
            denominator = term[1] - term[0]

            if abs(denominator) < 1e-10:
                self.print(f"\t{v} 计算分母接近零，无法计算")

            self.print(f"\t波数: {v}")
            self.print(f"\t折射率: {n}")
            self.print(f"\tsin θ: {sin_theta}")
            self.print(f"\tcos θ: {cos_theta}")

            m1 = numerator / denominator
            m2 = m1 + 1

            thickness_cm = (m1 + offset) / (2 * n[0] * v[0] * cos_theta[0])
            thickness_um = thickness_cm * 1e4

            thickness_history.append(thickness_um)

            detail = {
                'wavecount_pair': (v[0], v[1]),
                'm': m1,
                'thickness_um': thickness_um
            }

            thickness_details.append(detail)

            self.print(f"{detail}")

        if len(thickness_history) == 0:
            self.print("无有效厚度计算结果")
            return [], []
        
        thickness_avg = mean(thickness_history)
        thickness_std = std(thickness_history) if len(thickness_history) > 1 else 0

        self.print(f"'{method}' 厚度计算汇总:")
        print(f"\t有效结果数: {len(thickness_history)}")
        print(f"\t平均厚度: {thickness_avg:.3f} ± {thickness_std:.3f} μm")

        return thickness_history, thickness_details

    def analyze(self, filepath: str, incident_angle):
        """分析单个数据集"""
        self.print("=" * 30)
        self.print(f"目标文件: {filepath}")
        self.print('-' * 30)

        self.print("读取数据")
        w, r = self.read_data(filepath)
        if w is None:
            return None
        
        max_w, max_r, min_w, min_r = self.find_ex(w, r)
        self.print('-' * 30)

        self.print("对极大值计算厚度")
        thickness_for_max, details_max = self.calculate_thickness(max_w, incident_angle, 'max')
        self.print("对极小值计算厚度")
        thickness_for_min, details_min = self.calculate_thickness(min_w, incident_angle, 'min')

        self.print("=" * 30)

        return Result(
            filepath,
            incident_angle,
            w, r, max_w, min_w, max_r, min_r,
            thickness_for_max, thickness_for_min, details_max, details_min
        )
    
class Result:
    def __init__(self, filepath, incident_angle, wavecount, reflectence,
                 max_wavecount, min_wavecount, max_reflectence, min_reflectence,
                 thickness_for_max, thickness_for_min, details_for_max, details_for_min):
        self.filepath = filepath
        self.incident_angle = incident_angle
        self.wavecount = wavecount
        self.reflectence = reflectence
        self.max_wavecount = max_wavecount
        self.min_wavecount = min_wavecount
        self.max_reflectence = max_reflectence
        self.min_reflectence = min_reflectence
        self.thickness_for_max = thickness_for_max
        self.thickness_for_min = thickness_for_min
        self.details_for_max = details_for_max
        self.details_for_min = details_for_min
