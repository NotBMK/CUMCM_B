from .args import CustomParser
from .plot import Ploter
from .calc import Analyzer, mean, std

if __name__ == '__main__':
    args = CustomParser.load_params()

    print(args)

    analyzer = Analyzer(args)

    results = []
    all_thickness = []

    plot = Ploter()

    for (i, filepath) in enumerate(args.files):
        angle = args.angles[i]

        result = analyzer.analyze(filepath, angle)

        plot.append(result)

        if result:
            results.append(result)

            all_thickness.extend(result.thickness_for_max)
            all_thickness.extend(result.thickness_for_min)

    if len(all_thickness) > 0:
        print("计算结果如下:")
        print(f"总有效结果数: {len(all_thickness)}")
        print(f"厚度计算值: {[f'{t:.3f}' for t in all_thickness]}")

        if len(all_thickness) > 1:
            all_avg = mean(all_thickness)
            all_std = std(all_thickness)
            print(f"厚度估计值: {all_avg:.3f} ± {all_std:.3f} μm")

        with open("calc.log", "a", encoding="UTF8") as log_file:
            import datetime
            now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds')
            print(f"运行时间: {now}", file=log_file)
            if all_avg:
                print(f"厚度估计值: {all_avg:.3f} ± {all_std:.3f} μm", file=log_file)
            print(f"所有计算结果: {all_thickness}", file=log_file)
            for (i, r) in enumerate(results):
                print(f"数据文件: \"{r.filepath}\", 入射角: {r.incident_angle}", file=log_file)
                if len(r.thickness_for_max) > 0:
                    avg_max = mean(r.thickness_for_max)
                    std_max = std(r.thickness_for_max)
                    print(f"\t基于最大值计算得到的平均厚度: {avg_max:.3f} ± {std_max:.3f} μm", file=log_file)
                if len(r.thickness_for_min) > 0:
                    avg_min = mean(r.thickness_for_min)
                    std_min = std(r.thickness_for_min)
                    print(f"\t基于最小值计算得到的平均厚度: {avg_min:.3f} ± {std_min:.3f} μm", file=log_file)
            print(file=log_file)
        print("计算结束，结果已存至'calc.log'")

    plot.plot(args)