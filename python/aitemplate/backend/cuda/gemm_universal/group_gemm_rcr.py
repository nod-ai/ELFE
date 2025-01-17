#  Copyright (c) Meta Platforms, Inc. and affiliates.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
"""
Codegen functions for group_gemm_rcr.
"""
import jinja2

from ... import registry
from . import common, group_common
from .layout import RCR

# pylint: disable=C0103,C0415,W0613,C0301,R1705,R1703

PROBLEM_ARGS_TEMPLATE = jinja2.Template(
    """
        problem_sizes_device,
        problem_count,
        threadblock_count,
        {ElementComputeEpilogue(1), ElementComputeEpilogue(0)},
        ptr_A,
        ptr_B,
        ptr_C,
        ptr_C,
        lda,
        ldb,
        ldc,
        ldc
"""
)


@registry.reg("cuda.group_gemm_rcr.config")
def group_rcr_config(func_attrs, dtype="float16"):
    common.make_fproc_f16(func_attrs, RCR)


@registry.reg("cuda.group_gemm_rcr.gen_profiler")
def gen_profiler(func_attrs, workdir, shape_template):
    group_common.gen_profiler(
        func_attrs, workdir, shape_template, PROBLEM_ARGS_TEMPLATE
    )


@registry.reg("cuda.group_gemm_rcr.gen_function")
def gen_function(
    func_attrs,
    exec_cond_template,
    shape_eval_template,
):
    return group_common.gen_function(
        func_attrs,
        exec_cond_template,
        shape_eval_template,
        PROBLEM_ARGS_TEMPLATE,
    )


@registry.reg("cuda.group_gemm_rcr.func_decl")
def gen_function_decl(func_attrs):
    func_name = func_attrs["name"]
    return group_common.FUNC_DECL_TEMPLATE.render(
        func_name=func_name, groups=func_attrs["groups"]
    )


@registry.reg("cuda.group_gemm_rcr.func_call")
def gen_function_call(func_attrs, indent="  "):
    ndims = 2
    return group_common.gen_function_call(func_attrs, ndims)


@registry.reg("cuda.group_gemm_rcr.filter")
def function_filter(cfg, func_attrs, ab_alignment):
    """Generates function filter.

    Parameters
    ----------
    cfg: str
        The filename generated for profiler.
    func_attrs : Dict
        Stores the operation attributes.
    ab_alignment:
        Input alignments.

    Returns
    -------
    bool
        If input cfg should be filtered.
    """
    return common.function_filter(cfg, func_attrs, ab_alignment)
