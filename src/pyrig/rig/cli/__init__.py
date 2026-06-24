"""Command-line interface layer for pyrig and any project built on pyrig.

Commands are discovered at runtime from two sources: the calling project's own
command definitions, and a shared pool gathered from every installed package in
the pyrig dependency chain. This means any dependent package can contribute
commands that appear automatically in every project that depends on it, without
requiring changes to either pyrig or the target project.
"""
