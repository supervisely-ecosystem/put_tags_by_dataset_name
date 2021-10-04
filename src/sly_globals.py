import os
from pathlib import Path
import sys
import supervisely_lib as sly
import pickle


app = sly.AppService()
api = app.public_api
task_id = app.task_id

team_id = int(os.environ['context.teamId'])
workspace_id = int(os.environ['context.workspaceId'])
project_id = int(os.environ['modal.state.slyProjectId'])

project_info = api.project.get_info_by_id(project_id)
datasets_info = api.dataset.get_list(project_id)


if project_info is None:  # for debug
    raise ValueError(f"Project with id={project_id} not found")

#sly.fs.clean_dir(app.data_dir)  # @TODO: for debug

project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project_id))

automatically_tagged_class = sly.ObjClass('automatically_tagged_class', sly.Rectangle)
datasets_names = [curr_dataset.name for curr_dataset in datasets_info]
