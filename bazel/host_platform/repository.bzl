def _cpu_constraint(arch):
    if arch in ["amd64", "x64", "x86_64"]:
        return "x86_64"
    if arch == "aarch64":
        return "aarch64"
    return None

def _os_constraint(name):
    if name.startswith("linux"):
        return "linux"
    return None

def _host_platform_repo_impl(ctx):
    constraints = []

    cpu = _cpu_constraint(ctx.os.arch)
    if cpu:
        constraints.append("@platforms//cpu:%s" % cpu)

    os = _os_constraint(ctx.os.name)
    if os:
        constraints.append("@platforms//os:%s" % os)

    ctx.file("BUILD.bazel", "exports_files([\"constraints.bzl\"])\n")
    ctx.file(
        "constraints.bzl",
        "HOST_CONSTRAINTS = %s\n" % repr(constraints),
    )

host_platform_repo = repository_rule(
    implementation = _host_platform_repo_impl,
    local = True,
)
