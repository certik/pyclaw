import sys

def build_run_verify(path, target_name, module_name, method_name, verifier, options):
    sys.path.append(path)
    try:    
        build_command = "make -B -C %s %s" % (path, target_name)
        build_info = "[path: %s, name: %s]" % (path, target_name)
        build_it(build_info, build_command)
        module = __import__(module_name)
        run_method = getattr(module,method_name)
        
        # need a better way to branch
        if options.has_key('np') and options['np'] >1:
            verify_it_parallel(run_method, method_name, module_name, verifier, options, path)
        else:
            if options.has_key('np'): options.pop('np')
            verify_it(run_method, method_name, module_name, verifier, options, path)
    
    finally:
        sys.path.remove(path)
        if module_name in sys.modules:
            del(sys.modules[module_name])
            del module

def run_verify(path, module_name, method_name, verifier, options):
    """For tests that need no build (pure Python)"""
    sys.path.append(path)
    try:    
        module = __import__(module_name)
        run_method = getattr(module,method_name)
        verify_it(run_method, method_name, module_name, verifier, options, path)
    finally:
        sys.path.remove(path)
        if module_name in sys.modules:
            del(sys.modules[module_name])
            del module


def build_it(build_info, build_command):
    import subprocess, sys
    p = subprocess.Popen(build_command, executable='/bin/bash',shell=True, stdout=subprocess.PIPE ,stderr=subprocess.STDOUT)
    (stdout_data, ignore) = p.communicate()
    rc = p.returncode
    
    if rc is not None and rc % 256:
        err = "Error building %s\n" % (build_info)
        sys.stderr.write(err)
        sys.stderr.write(build_command)
        sys.stderr.write(stdout_data)
        raise BuildError(err)
 
def verify_it(run_method, method_name, module_name, verifier, options, path):
    output = run_method(**options)

    if not verifier(output):
        err = "Error verifying %s\n" % method_name
        sys.stderr.write("output: %s\n" % output)
        raise VerifyError(err)
    return

def verify_it_parallel(run_method, method_name, module_name, verifier, options, path):
    import subprocess
    import tempfile
    import shutil
    from pyclaw.solution import Solution
    # Create temp directory to write the output to and read it from
    outdir =  tempfile.mkdtemp()
    
    # run subprocess with the required number of processes
    option_string= ""
    for k in options:
        if k != 'np':
            if isinstance(options[k], str):
                option_string += k+"='"+str(options[k])+"',"
            else:
                option_string += k+"="+str(options[k])+","

    option_string += 'outdir = "'+outdir+'"' 

    run_command = "mpiexec", "-n", str(options['np']) ,"python","-c", "import sys; sys.path.append('"+path+"'); import "+module_name+"; "+module_name+"."+method_name+"("+option_string+")"
    p = subprocess.Popen(run_command, stdout=subprocess.PIPE ,stderr=subprocess.STDOUT)
    (stdout_data, ignore) = p.communicate()

    ## example specific, need to generlize frame number which is 10 in this case
    output = Solution(options['nout'], format='petsc', path=outdir )

    # Remove the temporary output directory
    shutil.rmtree(outdir) 
    
    if not verifier(output):
        err = "Error verifying %s\n" % method_name
        sys.stderr.write("output: %s\n" % output)
        raise VerifyError(err)
    return


class Error(Exception):
    def __init__(self, expr):
        self.expr = expr
    def __str__(self):
        return repr(self.expr)

class BuildError(Exception):
    pass

class VerifyError(Exception):
    pass