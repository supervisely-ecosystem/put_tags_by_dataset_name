import supervisely_lib as sly

from tqdm import tqdm
import sly_globals as g


def update_meta():
    temp_project_meta = sly.ProjectMeta(obj_classes=sly.ObjClassCollection([g.automatically_tagged_class]),
                                        project_type='images',
                                        tag_metas=sly.TagMetaCollection([
                                            sly.TagMeta(f"{dataset_name}", sly.TagValueType.NONE) for dataset_name in
                                            g.datasets_names
                                        ]))

    g.project_meta = g.project_meta.merge(temp_project_meta)

    g.api.project.update_meta(g.project_id, g.project_meta.to_json())


def main():
    update_meta()

    batch_size = 1024

    images_ids = []
    annotations_to_upload = []

    for dataset_index, current_dataset in tqdm(enumerate(g.datasets_info), total=len(g.datasets_info),
                                               desc=f'processing datasets'):
        images_in_dataset_info = g.api.image.get_list(current_dataset.id)
        # for image_info in tqdm(images_in_dataset_info, total=len(images_in_dataset_info),
        #                        desc=f'processing dataset {dataset_index}/{len(g.datasets_info)}'):
        for image_info in images_in_dataset_info:
            label_picture = sly.Label(sly.Rectangle(top=0, left=0,
                                                    bottom=image_info.height - 1, right=image_info.width - 1),
                                      g.automatically_tagged_class,
                                      tags=sly.TagCollection([
                                          sly.Tag(g.project_meta.get_tag_meta(f"{current_dataset.name}"))
                                      ]))

            current_ann = sly.Annotation((image_info.height, image_info.width), [label_picture])

            images_ids.append(image_info.id)
            annotations_to_upload.append(current_ann.to_json())

            if len(images_ids) > 0 and len(images_ids) % batch_size == 0:
                g.api.annotation.upload_jsons(images_ids, annotations_to_upload)
                images_ids = []
                annotations_to_upload = []

        if len(images_ids) > 0:
            g.api.annotation.upload_jsons(images_ids, annotations_to_upload)
            images_ids = []
            annotations_to_upload = []

    if len(images_ids) > 0:
        g.api.annotation.upload_jsons(images_ids, annotations_to_upload)


if __name__ == "__main__":
    sly.main_wrapper("main", main)
