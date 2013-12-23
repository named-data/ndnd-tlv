# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-
VERSION='0.3~dev0'
NAME="ndn-tlv-daemon"

from waflib import Build, Logs, Utils, Task, TaskGen, Configure

def options(opt):
    opt.load('compiler_c compiler_cxx gnu_dirs')
    opt.load('openssl boost', tooldir=['waf-tools'])

    opt = opt.add_option_group('NDN TLV Daemon Options')
    opt.add_option('--debug',action='store_true',default=False,dest='debug',help='''debugging mode''')

def configure(conf):
    conf.load("compiler_c compiler_cxx gnu_dirs openssl boost")

    conf.find_program('sh')
    
    if conf.options.debug:
        conf.define ('_DEBUG', 1)
        flags = ['-O0',
                 '-Wall',
                 '-Wno-unused-variable',
                 '-g3',
                 '-Wno-unused-private-field', # only clang supports
                 '-fcolor-diagnostics',       # only clang supports
                 '-Qunused-arguments',        # only clang supports
                 '-Wno-deprecated-declarations',
                 ]

        conf.add_supported_cxxflags (cxxflags = flags)
        conf.add_supported_cflags (cflags = flags)
    else:
        flags = ['-O3', '-g', '-Wno-tautological-compare', '-Wno-unused-function', '-Wno-deprecated-declarations']
        conf.add_supported_cxxflags (cxxflags = flags)
        conf.add_supported_cflags (cflags = flags)

    conf.define ("PACKAGE_BUGREPORT", "ndn-lib@lists.cs.ucla.edu")
    conf.define ("PACKAGE_NAME", NAME)
    conf.define ("PACKAGE_VERSION", VERSION)
    # conf.define ("PACKAGE_URL", "https://github.com/named-data/ndn-cpp")

    conf.check_openssl()
    # conf.check_cxx(lib='ndn-cpp-dev', uselib_store='NDN_CPP', mandatory=True)
    conf.check_boost(lib="system iostreams")

def build (bld):
    bld (target = 'libc',
         features=['c', 'cxx'],
         source = bld.path.ant_glob(['lib/**/*.c', 'tlv-hack/**/*.cpp']),
         use = 'OPENSSL BOOST',
         includes = "include",
         )

    bld (target="bin/ndnd-tlv",
         features=['c', 'cxx', 'cxxprogram'],
         source = bld.path.ant_glob(['ndnd/**/*.c', 'ndnd/**/*.cpp']),
         use = 'libc OPENSSL BOOST NDN_CPP',
         includes = "include",
        )

    for app in bld.path.ant_glob('bin/*.c'):
        bld(features=['c', 'cxxprogram'],
            target = app.change_ext('','.c'),
            source = app,
            use = 'libc BOOST OPENSSL',
            includes = "include",
            )

    bld (features = "subst",
         source = bld.path.ant_glob(['bin/**/*.sh']),
         target = [node.change_ext('', '.sh') for node in bld.path.ant_glob(['bin/**/*.sh'])],
         install_path = "${BINDIR}",
         chmod = 0755,
        )        
        
@Configure.conf
def add_supported_cxxflags(self, cxxflags):
    """
    Check which cxxflags are supported by compiler and add them to env.CXXFLAGS variable
    """
    self.start_msg('Checking allowed flags for c++ compiler')

    supportedFlags = []
    for flag in cxxflags:
        if self.check_cxx (cxxflags=[flag], mandatory=False):
            supportedFlags += [flag]

    self.end_msg (' '.join (supportedFlags))
    self.env.CXXFLAGS += supportedFlags

@Configure.conf
def add_supported_cflags(self, cflags):
    """
    Check which cflags are supported by compiler and add them to env.CFLAGS variable
    """
    self.start_msg('Checking allowed flags for c compiler')

    supportedFlags = []
    for flag in cflags:
        if self.check_cc (cflags=[flag], mandatory=False):
            supportedFlags += [flag]

    self.end_msg (' '.join (supportedFlags))
    self.env.CFLAGS += supportedFlags
