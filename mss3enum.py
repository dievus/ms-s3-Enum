import urllib3
from functions.args import arg_handler
from functions.auth import auth_func
from functions.unauth import unauth_func

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def banner():

    print("┌┬┐┌─┐  ╔═╗3  ╔═╗┌┐┌┬ ┬┌┬┐")
    print("│││└─┐  ╚═╗   ║╣ ││││ ││││")
    print("┴ ┴└─┘  ╚═╝   ╚═╝┘└┘└─┘┴ ┴")
    print("Private/Public")
    print("S3 File Downloader and More")
    print("Another tool by The Mayor\n")


if __name__ == "__main__":
    global args
    banner()
    args = arg_handler()
    bucket = ""
    if args.bucket:
        bucket = args.bucket
    else:
        bucket = bucket
    if args.accesskey and args.secretkey:
        if args.recursive and bucket:
            print(f"Initiating authenticated, recursive enumeration of {bucket}")
            print("-" * 125)
            auth_func(args, bucket)
        elif bucket:
            print(f"Initiating authenticated enumeration of {bucket}")
            print("-" * 125)
            auth_func(args, bucket)
        else:
            print(f"Initiating authenticated enumeration of available information.")
            print("-" * 125)
            auth_func(args, bucket)            
    else:
        if args.recursive and bucket:
            print(f"Initiating unauthenticated, recursive enumeration of {bucket}")
            print("-" * 125)
            unauth_func(args, bucket)
        elif bucket:
            print(f"Initiating unauthenticated enumeration of {bucket}")
            print("-" * 125)
            unauth_func(args, bucket)
        else:
            print(f"Initiating unauthenticated enumeration of available information.")    
            print("-" * 125)
            unauth_func(args, bucket)