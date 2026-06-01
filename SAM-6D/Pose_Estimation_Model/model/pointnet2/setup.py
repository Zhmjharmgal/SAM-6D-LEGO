# Copyright (c) Facebook, Inc. and its affiliates.
# 
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
import shutil
import site
from pathlib import Path
from setuptools import setup, find_packages
import glob


def _find_nvidia_runtime_hint():
    for site_dir in site.getsitepackages():
        runtime_include = Path(site_dir) / "nvidia" / "cuda_runtime" / "include" / "cuda.h"
        if runtime_include.exists():
            return runtime_include.parent.parent
    return None


def _cuda_home_candidates():
    for env_name in ("CUDA_HOME", "CUDA_PATH"):
        cuda_home = os.environ.get(env_name)
        if cuda_home:
            yield Path(cuda_home)

    nvcc = shutil.which("nvcc")
    if nvcc:
        yield Path(nvcc).resolve().parent.parent

    yield Path("/usr/local/cuda")
    yield from sorted(Path("/usr/local").glob("cuda-*"), reverse=True)


def _has_nvcc(cuda_home):
    return (cuda_home / "bin" / "nvcc").is_file()


def _configure_cuda_home():
    cuda_home_env = os.environ.get("CUDA_HOME")
    if cuda_home_env:
        cuda_home = Path(cuda_home_env)
        if _has_nvcc(cuda_home):
            return
        raise RuntimeError(
            f"CUDA_HOME is set to {cuda_home}, but {cuda_home / 'bin' / 'nvcc'} "
            "does not exist. Set CUDA_HOME to a CUDA toolkit directory that "
            "contains bin/nvcc."
        )

    for cuda_home in _cuda_home_candidates():
        if _has_nvcc(cuda_home):
            os.environ["CUDA_HOME"] = str(cuda_home)
            return

    runtime_hint = _find_nvidia_runtime_hint()
    runtime_text = (
        f"\nFound CUDA runtime headers at {runtime_hint}, but the runtime "
        "wheel does not include nvcc."
        if runtime_hint
        else ""
    )
    raise RuntimeError(
        "Building pointnet2 requires a CUDA toolkit with nvcc, but no nvcc "
        "was found and CUDA_HOME is not set."
        f"{runtime_text}\nInstall a CUDA toolkit that matches PyTorch's CUDA "
        "version, or set CUDA_HOME to an existing CUDA toolkit directory "
        "(for example: export CUDA_HOME=/usr/local/cuda)."
    )


_configure_cuda_home()

from torch.utils.cpp_extension import BuildExtension, CUDAExtension

_this_dir = Path(__file__).resolve().parent
_ext_src_root = _this_dir / "_ext_src"
_ext_sources = glob.glob(str(_ext_src_root / "src" / "*.cpp")) + glob.glob(
    str(_ext_src_root / "src" / "*.cu")
)
_ext_headers = glob.glob(str(_ext_src_root / "include" / "*"))

setup(
    name='pointnet2',
    packages = find_packages(),
    ext_modules=[
        CUDAExtension(
            name='pointnet2._ext',
            sources=_ext_sources,
            include_dirs = [str(_ext_src_root / "include")],
            extra_compile_args={
                # "cxx": ["-O2", "-I{}".format("{}/include".format(_ext_src_root))],
                # "nvcc": ["-O2", "-I{}".format("{}/include".format(_ext_src_root))],
                "cxx": [],
                "nvcc": ["-O3", 
                "-DCUDA_HAS_FP16=1",
                "-D__CUDA_NO_HALF_OPERATORS__",
                "-D__CUDA_NO_HALF_CONVERSIONS__",
                "-D__CUDA_NO_HALF2_OPERATORS__",
            ]},)
    ],
    cmdclass={'build_ext': BuildExtension.with_options(use_ninja=True)}
)
