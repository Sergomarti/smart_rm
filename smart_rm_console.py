import smart_rm
import argparse


def console(trash_can: smart_rm.SmartRm):
    parser = argparse.ArgumentParser(description='Welcome to the trash bin')
    parser.add_argument('path', type=str, nargs='?', help='The path to the file')
    parser.add_argument('-rm', '--remove', action='store_true', help='Move unnecessary files to the trash')
    parser.add_argument('-rs', '--restore', action='store_true', help='Return deleted files')
    parser.add_argument('-in', '--info', action='store_true', help='Show all information about files in can')
    parser.add_argument('-ca', '--clear_all', action='store_true', help='Delete all files permanently')
    parser.add_argument('-cl', '--clear', action='store_true', help='Delete files permanently')
    args = parser.parse_args()

    if args.remove:
        if not args.path:
            print('Path not entering')
            return
        try:
            trash_can.way_trash_bin(args.path)
        except FileExistsError as error:
            print(error)
        else:
            print(f'File {args.path} placed in the trash bin')
    elif args.restore:
        if not args.path:
            print('Trash not entering')
            return
        try:
            trash_can.restore_file(args.path)
        except FileExistsError as error:
            print(error)
        else:
            print(f'File {args.path} was reborn')
    elif args.clear:
        if not args.path:
            print('Trash not entering')
            return
        try:
            trash_can.delete_forever(args.path)
        except FileExistsError as error:
            print(error)
        else:
            print(f'File {args.path} permanently deleted')
    elif args.clear_all:
        try:
            trash_can.clear_all_trash()
        except FileExistsError as error:
            print(error)
        else:
            print('Trash all cleared')
    elif args.info:
        print(trash_can.trash_info())


if __name__ == '__main__':
    user_trash_can = smart_rm.SmartRm()
    console(user_trash_can)
