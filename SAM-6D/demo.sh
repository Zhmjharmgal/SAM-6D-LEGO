set -eu

PROJECT_ROOT=$(pwd)
case "$CAD_PATH" in /*) ;; *) CAD_PATH="$PROJECT_ROOT/$CAD_PATH" ;; esac
case "$RGB_PATH" in /*) ;; *) RGB_PATH="$PROJECT_ROOT/$RGB_PATH" ;; esac
case "$DEPTH_PATH" in /*) ;; *) DEPTH_PATH="$PROJECT_ROOT/$DEPTH_PATH" ;; esac
case "$CAMERA_PATH" in /*) ;; *) CAMERA_PATH="$PROJECT_ROOT/$CAMERA_PATH" ;; esac
case "$OUTPUT_DIR" in /*) ;; *) OUTPUT_DIR="$PROJECT_ROOT/$OUTPUT_DIR" ;; esac

mkdir -p "$OUTPUT_DIR"
BLENDER_INSTALL_PATH="${BLENDER_INSTALL_PATH:-$PROJECT_ROOT/.cache/blender}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$PROJECT_ROOT/.cache/matplotlib}"
mkdir -p "$MPLCONFIGDIR"

# Render CAD templates
cd Render
if [ "${BLENDERPROC_FORCE_PIP_UPDATE:-0}" = "1" ]; then
    blenderproc run --blender-install-path "$BLENDER_INSTALL_PATH" --force-pip-update render_custom_templates.py --output_dir "$OUTPUT_DIR" --cad_path "$CAD_PATH" #--colorize True
else
    blenderproc run --blender-install-path "$BLENDER_INSTALL_PATH" render_custom_templates.py --output_dir "$OUTPUT_DIR" --cad_path "$CAD_PATH" #--colorize True
fi


# Run instance segmentation model
export SEGMENTOR_MODEL="${SEGMENTOR_MODEL:-sam}"

cd ../Instance_Segmentation_Model
python run_inference_custom.py --segmentor_model "$SEGMENTOR_MODEL" --output_dir "$OUTPUT_DIR" --cad_path "$CAD_PATH" --rgb_path "$RGB_PATH" --depth_path "$DEPTH_PATH" --cam_path "$CAMERA_PATH"


# Run pose estimation model
export SEG_PATH=$OUTPUT_DIR/sam6d_results/detection_ism.json

cd ../Pose_Estimation_Model
python run_inference_custom.py --output_dir "$OUTPUT_DIR" --cad_path "$CAD_PATH" --rgb_path "$RGB_PATH" --depth_path "$DEPTH_PATH" --cam_path "$CAMERA_PATH" --seg_path "$SEG_PATH"
