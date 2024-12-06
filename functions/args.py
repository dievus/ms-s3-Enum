import argparse
import textwrap
import sys
def arg_handler():
    opt_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""python3 mss3enum.py """),
    )
    opt_parser_target = opt_parser.add_argument_group("Target S3 Bucket")
    opt_parser_target.add_argument(
        "-b", "--bucket", help="Sets the S3 bucket name to enumerate."
    )
    opt_parser_anon = opt_parser.add_argument_group("Anonymous Enumeration")
    opt_parser_anon.add_argument(
        "-a",
        "--anon",
        help="Checks for files available with anonymous access.",
        action="store_true",
    )
    opt_parser_auth = opt_parser.add_argument_group("Authenticated Enumeration")
    opt_parser_auth.add_argument(
        "-ak", "--accesskey", help="Sets the AWS access key to use."
    )
    opt_parser_auth.add_argument(
        "-sk", "--secretkey", help="Sets the AWS secret key to use."
    )
    opt_parser_auth.add_argument(
        "-st", "--sesstoken", help="Sets the AWS Session Token to use."
    )
    opt_parser_additional_options = opt_parser.add_argument_group("Additional Options")
    opt_parser_additional_options.add_argument(
        "-rc", "--recursive", help="Scans the bucket recursively", action="store_true"
    )
    opt_parser_additional_options.add_argument(
        "-u", "--unsigned", help="Removes signing from requests", action="store_true"
    )
    opt_parser_target.add_argument(
        "-r", "--region", help="Specifies the region to use."
    )

    global args
    args = opt_parser.parse_args()
    if len(sys.argv) <= 1:
        opt_parser.print_help()
        opt_parser.exit()
    return args