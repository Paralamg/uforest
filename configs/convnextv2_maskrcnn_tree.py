
_base_ = [
    'mmdet::_base_/models/mask-rcnn_r50_fpn.py',
    'mmdet::_base_/datasets/coco_instance.py',
    'mmdet::_base_/schedules/schedule_1x.py',
    'mmdet::_base_/default_runtime.py'
]

custom_imports = dict(
    imports=['mmpretrain.models'], allow_failed_imports=False)

checkpoint_file = 'https://download.openmmlab.com/mmclassification/v0/convnext-v2/convnext-v2-base_3rdparty-fcmae_in1k_20230104-8a798eaf.pth'  # noqa
image_size = (2048, 2048)

work_dir = '../models/convnextv2_maskrcnn_tree'
model = dict(
    backbone=dict(
        _delete_=True,
        type='mmpretrain.ConvNeXt',
        arch='base',
        out_indices=[0, 1, 2, 3],
        drop_path_rate=0.4,
        layer_scale_init_value=0.,
        gap_before_final_norm=False,
        use_grn=True,
        init_cfg=dict(
            type='Pretrained', checkpoint=checkpoint_file,
            prefix='backbone.')),
    neck=dict(in_channels=[128, 256, 512, 1024]),
    roi_head=dict(
        bbox_head=dict(num_classes=1),
        mask_head=dict(num_classes=1),
    ),
    test_cfg=dict(
        rpn=dict(nms=dict(type='nms')),
        rcnn=dict(nms=dict(type='soft_nms')))
)

dataset_type = 'CocoDataset'
classes = ('tree',)
data_root = '../data/Bamberg_coco2048/coco2048'

            
train_pipeline = [
    dict(type='LoadImageFromFile', backend_args=_base_.backend_args),
    dict(type='LoadAnnotations', with_bbox=True, with_mask=True),
    # dict(
    #     type='RandomResize',
    #     scale=image_size,
    #     ratio_range=(0.1, 2.0),
    #     keep_ratio=True),
    # dict(
    #     type='RandomCrop',
    #     crop_type='absolute_range',
    #     crop_size=image_size,
    #     recompute_bbox=True,
    #     allow_negative_crop=True),
    # dict(type='FilterAnnotations', min_gt_bbox_wh=(1e-2, 1e-2)),
    dict(type='RandomFlip', prob=0.5),
    dict(type='PackDetInputs')
]

train_dataloader = dict(
    batch_size=2,  # total_batch_size 32 = 8 GPUS x 4 images
    num_workers=1,
    dataset=dict(pipeline=train_pipeline,
                ann_file='annotations/instances_tree_train2023.json',
                backend_args=None,
                data_prefix=dict(img='train2023/'),
                data_root=data_root,
))
            
val_dataloader = dict(
    batch_size=2,  # total_batch_size 32 = 8 GPUS x 4 images
    num_workers=1,
    dataset=dict(pipeline=train_pipeline,
                ann_file='annotations/instances_tree_eval2023.json',
                backend_args=None,
                data_prefix=dict(img='val2023/'),
                data_root=data_root,
))


test_dataloader = val_dataloader

train_cfg = dict(max_epochs=36)

param_scheduler = [
    dict(type='LinearLR', start_factor=0.001, by_epoch=False, begin=0, end=1000),
    dict(type='MultiStepLR', begin=0, end=36, by_epoch=True, milestones=[27, 33], gamma=0.1)
]

optim_wrapper = dict(
    type='AmpOptimWrapper',
    constructor='LearningRateDecayOptimizerConstructor',
    paramwise_cfg={
        'decay_rate': 0.95,
        'decay_type': 'layer_wise',
        'num_layers': 12
    },
    optimizer=dict(
        _delete_=True,
        type='AdamW',
        lr=0.0001,
        betas=(0.9, 0.999),
        weight_decay=0.05
    )
)

default_hooks = dict(checkpoint=dict(max_keep_ckpts=1))

# Используем COCO AP метрики
val_evaluator = dict(type='CocoMetric', ann_file=data_root + 'annotations/instances_tree_eval2023.json', metric=['bbox', 'segm'])
test_evaluator = val_evaluator

default_scope = 'mmdet'
