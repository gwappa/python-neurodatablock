#
# MIT License
#
# Copyright (c) 2020 Keisuke Sehara
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import pathlib as _pathlib

from .. import modes as _modes
from .. import levels as _levels
from .. import core as _core
from .. import dataio as _dataio

from ..predicate import Predicate as _Predicate
from ..sessionspec import SessionSpec as _SessionSpec
from ..filespec import FileSpec as _FileSpec

def validate(spec, mode=None):
    """`spec` may be a path-like object or a Predicate.
    by default, dope.modes.READ is selected for `mode`."""
    if not isinstance(spec, _Predicate):
        try:
            path = _pathlib.Path(spec).resolve()
        except TypeError:
            raise ValueError(f"Datafile can only be initialized by a path-like object or a Predicate, not {spec.__class__}")
        domdir  = path.parent
        sessdir = domdir.parent
        subdir  = sessdir.parent
        root    = subdir.parent
        spec = _Predicate(root=root,
                          subject=subdir.name,
                          session=_SessionSpec(sessdir.name),
                          domain=domdir.name,
                          file=_FileSpec(path.name))
    if mode is not None:
        spec = spec.with_values(mode=_mode.validate(mode))
    return spec

class Datafile(_core.Container):
    """a container class representing a data file."""

    def __init__(self, spec, mode=None):
        """`spec` may be a Datafile, a path-like object or a Predicate.
        by default, dope.modes.READ is selected for `mode`."""
        if isinstance(spec, Datafile):
            spec = spec._spec
        spec  = validate(spec, mode=mode)
        level = spec.level
        if level != _levels.FILE:
            raise ValueError(f"cannot specify a data file from the predicate level: '{level}'")

        self._spec = spec
        self._path = spec.compute_path()
        if (self._spec.mode == _modes.READ) and (not self._path.exists()):
            raise FileNotFoundError(f"data file does not exist: {self._path}")

    @property
    def level(self):
        return _levels.FILE

    @property
    def name(self):
        return self._spec.file.format_name(self._spec)

    @property
    def trial(self):
        if self._spec.file.blocktype != "trial":
            raise ValueError("this datafile is not specified as trial-related")
        return self._spec.file.index

    @property
    def run(self):
        if self._spec.file.blocktype != "run":
            raise ValueError("this datafile is not specified in terms of runs")
        return self._spec.file.index

    @property
    def blocktype(self):
        return self._spec.file.blocktype

    @property
    def index(self):
        return self._spec.file.index

    @property
    def channel(self):
        return self._spec.file.channel

    @property
    def suffix(self):
        return self._spec.file.suffix

    @property
    def file_specs(self):
        return self._spec.file

    @property
    def dataset(self):
        from ..dataset import Dataset
        return Dataset(self._spec.as_dataset())

    @property
    def subject(self):
        from ..subject import Subject
        return Subject(self._spec.as_subject())

    @property
    def session(self):
        from ..session import Session
        return Session(self._spec.as_session())

    @property
    def domain(self):
        from ..domain import Domain
        return Domain(self._spec.as_domain())

    def load(self, loader=None, **kwargs):
        return _dataio.load(self._spec, loader=loader, **kwargs)

    def save(self, data, loader=None, **kwargs):
        return _dataio.save(self._spec, data, loader=loader, **kwargs)
