from argparse import ArgumentParser, Namespace

class CustomParser(ArgumentParser):
    def parse_args(self, args=None, namespace=None):
        args_obj = super().parse_args(args, namespace)

        if len(args_obj.files) != len(args_obj.angles):
            self.error("'--files' 与 '--angles' 的参数个数必须相等且一一对应")

        return args_obj

    @staticmethod
    def load_params() -> Namespace:
        parser = CustomParser()

        parser.add_argument("--debug", "-d", action="store_true",
                            help="显示更多运行时信息")

        parser.add_argument("--files", nargs='+', type=str,
                            required=True,
                            help="给出两个输入文件")
        parser.add_argument("--angles", nargs='+', type=float,
                            help="对应文件的入射角")

        pk = parser.add_argument_group("peak detection")
        pk.add_argument("--min-wavecount", type=int, default=1200)
        pk.add_argument("--max-wavecount", type=int, default=4000)
        pk.add_argument("--min-prominence", type=float, default=0.1)
        pk.add_argument("--max-prominence", type=float, default=0.1)
        pk.add_argument("--min-distance", type=int, default=200)
        pk.add_argument("--max-distance", type=int, default=200)
        pk.add_argument("--min-height-factor", type=float, default=0.9)
        pk.add_argument("--max-height-factor", type=float, default=-1.5)

        plt = parser.add_argument_group("plot settings")
        plt.add_argument("--figure-size", nargs=2, type=float, default=[14, 8], metavar=("W", "H"))
        plt.add_argument("--line-width", type=float, default=1.5)
        plt.add_argument("--max-marker-size", type=int, default=8)
        plt.add_argument("--min-marker-size", type=int, default=8)
        plt.add_argument("--font-size", type=int, default=12)
        plt.add_argument("--title-size", type=int, default=14)
        plt.add_argument("--annotation-size", type=int, default=9)

        return parser.parse_args()