import argparse
import os
import io

from label_studio_converter.converter import Converter, Format
from label_studio_converter import brush


class ExpandFullPath(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))


def main():
    parser = argparse.ArgumentParser(
        description='Converter from Label Studio output completions to various formats',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-i', '--input', dest='input', required=True,
        help='Directory or JSON file with completions (e.g. "/<project_path>/completions")',
        action=ExpandFullPath
    )
    parser.add_argument(
        '-c', '--config', dest='config', required=True,
        help='Project config (e.g. "/<project_path>/config.xml")',
        action=ExpandFullPath
    )
    parser.add_argument(
        '-o', '--output', dest='output',
        help='Output file or directory (will be created if not exists)',
        default=os.path.join(os.path.dirname(__file__), 'output'),
        action=ExpandFullPath
    )
    parser.add_argument(
        '-f', '--format', dest='format',
        metavar='FORMAT',
        help='Output format: ' + ', '.join(f.name for f in Format),
        type=Format.from_string,
        choices=list(Format),
        default=Format.JSON
    )
    parser.add_argument(
        '--csv-separator', dest='csv_separator',
        help='Separator used in CSV format',
        default=','
    )
    parser.add_argument(
        '--csv-no-header', dest='csv_no_header',
        help='Whether to omit header in CSV output file',
        action='store_true'
    )
    parser.add_argument(
        '--image-dir', dest='image_dir',
        help='In case of image outputs (COCO, VOC, ...), specifies output image directory where downloaded images will '
             'be stored. (If not specified, local image paths left untouched)'
    )
    parser.add_argument(
        '--project-dir', dest='project_dir', default=None,
        help='Label Studio project directory path'
    )
    parser.add_argument(
        '--heartex-format', dest='heartex_format', action='store_true',
        help='Set this flag if your completions are coming from Heartex platform instead of Label Studio'
    )
    args = parser.parse_args()

    with io.open(args.config) as f:
        config_str = f.read()
    c = Converter(config_str, project_dir=args.project_dir)

    if args.format == Format.JSON:
        c.convert_to_json(args.input, args.output)
    elif args.format == Format.CSV:
        header = not args.csv_no_header
        sep = args.csv_separator
        c.convert_to_csv(args.input, args.output, sep=sep, header=header, is_dir=False)
    elif args.format == Format.CONLL2003:
        c.convert_to_conll2003(args.input, args.output, is_dir=not args.heartex_format)
    elif args.format == Format.COCO:
        c.convert_to_coco(args.input, args.output, output_image_dir=args.image_dir, is_dir=not args.heartex_format)
    elif args.format == Format.VOC:
        c.convert_to_voc(args.input, args.output, output_image_dir=args.image_dir, is_dir=not args.heartex_format)
    elif args.format == Format.BRUSH_TO_PNG:
        items = c.iter_from_json_file(args.input)
        brush.convert_task_dir(items, args.output, out_format='png')

    print('Congratulations! Now check:\n' + args.output)


if __name__ == "__main__":
    main()
