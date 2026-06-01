#!/usr/bin/env bash
set -euo pipefail

uv sync

uv pip install --no-build-isolation ./Pose_Estimation_Model/model/pointnet2

uv run python Instance_Segmentation_Model/download_sam.py
uv run python Instance_Segmentation_Model/download_fastsam.py
uv run python Instance_Segmentation_Model/download_dinov2.py
uv run python Pose_Estimation_Model/download_sam6d-pem.py
