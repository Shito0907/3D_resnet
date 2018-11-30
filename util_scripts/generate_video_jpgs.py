import subprocess
import argparse
from pathlib import Path

from joblib import Parallel, delayed


def video_process(video_file_path, dst_root_path, ext, fps=-1, size=240):
    if ext != video_file_path.suffix:
        return
    name = video_file_path.stem
    dst_dir_path = dst_root_path / name

    if dst_dir_path.exists():
        return
    else:
        dst_dir_path.mkdir()

    ffprobe_cmd = [
        'ffprobe', '-hide_banner', '-show_entries', 'stream=width,height',
        str(video_file_path)
    ]
    p = subprocess.Popen(
        ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res = p.communicate()[0].decode('utf-8').split('\n')
    if len(res) <= 3:
        return
    width = int([x.split('=') for x in res if 'width' in x][0][1])
    height = int([x.split('=') for x in res if 'height' in x][0][1])

    if width > height:
        scale_param = '-1:{}'.format(size)
    else:
        scale_param = '{}:-1'.format(size)

    fps_param = ''
    if fps > 0:
        fps_param = ',fps={}'.format(fps)
    vf_param = '"scale={}{}"'.format(scale_param, fps_param)

    ffmpeg_cmd = [
        'ffmpeg', '-i',
        str(video_file_path), '-vf', vf_param, '-threads', '1',
        '{}/image_%05d.jpg'.format(dst_dir_path)
    ]
    print(ffmpeg_cmd)
    subprocess.call(ffmpeg_cmd)
    print('\n')


def class_process(class_dir_path, dst_root_path, ext, fps=-1):
    if not class_dir_path.is_dir():
        return

    dst_class_path = dst_root_path / class_dir_path.name
    dst_class_path.mkdir(exist_ok=True)

    for video_file_path in sorted(class_dir_path.iterdir()):
        video_process(video_file_path, dst_class_path, ext, fps)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'dir_path', default=None, type=Path, help='Directory path of videos')
    parser.add_argument(
        'dst_path',
        default=None,
        type=Path,
        help='Directory path of jpg videos')
    parser.add_argument(
        'dataset',
        default='',
        type=str,
        help='Dataset name (kinetics | mit | ucf101 | hmdb51 | activitynet)')
    parser.add_argument(
        '--n_jobs', default=-1, type=int, help='Number of parallel jobs')
    parser.add_argument(
        '--fps',
        default=-1,
        type=int,
        help=('Frame rates of output videos. '
              '-1 means original frame rates.'))
    parser.add_argument(
        '--size', default=240, type=int, help='Frame size of output videos.')
    args = parser.parse_args()

    if args.dataset in ['kinetics', 'mit', 'activitynet']:
        ext = '.mp4'
    else:
        ext = '.avi'

    if args.dataset == 'activitynet':
        video_file_paths = [x for x in sorted(args.dir_path.iterdir())]
        status_list = Parallel(
            n_jobs=args.n_jobs,
            backend='threading')(delayed(video_process)(video_file_path, args.
                                                        dst_path, ext, args.fps)
                                 for video_file_path in video_file_paths)
    else:
        class_dir_paths = [x for x in sorted(args.dir_path.iterdir())]
        test_set_video_path = args.dir_path / 'test'
        if test_set_video_path.exists():
            class_dir_paths.append(test_set_video_path)

        status_list = Parallel(
            n_jobs=args.n_jobs,
            backend='threading')(delayed(class_process)(
                class_dir_path, args.dst_path, ext, args.fps, args.size)
                                 for class_dir_path in class_dir_paths)
