from torch.utils.data.dataloader import default_collate

from datasets.videodataset import VideoDataset, multi_clips_collate_fn
from datasets.activitynet import ActivityNet


def get_training_set(video_path, annotation_path, dataset_name,
                     spatial_transform, temporal_transform, target_transform):
    assert dataset_name in [
        'kinetics', 'activitynet', 'ucf101', 'hmdb51', 'mit'
    ]

    if dataset_name == 'activitynet':
        training_data = ActivityNet(
            video_path,
            annotation_path,
            'training',
            spatial_transform=spatial_transform,
            temporal_transform=temporal_transform,
            target_transform=target_transform)
    else:
        training_data = VideoDataset(
            video_path,
            annotation_path,
            'training',
            spatial_transform=spatial_transform,
            temporal_transform=temporal_transform,
            target_transform=target_transform)

    return training_data, default_collate


def get_validation_set(video_path, annotation_path, dataset_name,
                       spatial_transform, temporal_transform, target_transform):
    assert dataset_name in [
        'kinetics', 'activitynet', 'ucf101', 'hmdb51', 'mit'
    ]

    if dataset_name == 'activitynet':
        validation_data = ActivityNet(video_path, annotation_path, 'validation',
                                      spatial_transform, temporal_transform,
                                      target_transform)
    else:
        validation_data = VideoDataset(
            video_path,
            annotation_path,
            'validation',
            spatial_transform=spatial_transform,
            temporal_transform=temporal_transform,
            target_transform=target_transform)

    return validation_data, multi_clips_collate_fn


def get_test_set(video_path, annotation_path, dataset_name, test_subset,
                 spatial_transform, temporal_transform, target_transform):
    assert dataset_name in [
        'kinetics', 'activitynet', 'ucf101', 'hmdb51', 'mit'
    ]
    assert test_subset in ['val', 'test']

    if test_subset == 'val':
        subset = 'validation'
    elif test_subset == 'test':
        subset = 'testing'
    if dataset_name == 'activitynet':
        test_data = ActivityNet(
            video_path,
            annotation_path,
            subset,
            spatial_transform,
            temporal_transform,
            target_transform,
            is_untrimmed_setting=True)
    else:
        test_data = VideoDataset(
            video_path,
            annotation_path,
            subset,
            spatial_transform=spatial_transform,
            temporal_transform=temporal_transform,
            target_transform=target_transform)

    return test_data, multi_clips_collate_fn
