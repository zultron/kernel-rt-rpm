%global __spec_install_pre %{___build_pre}

# Define the version of the Linux Kernel Archive tarball.
%define LKAver 3.8.13

# Find the Xenomai ipipe patch matching this kernel
%define ipipe_patchdir /usr/src/xenomai/ksrc/arch/x86/patches
%define ipipe_patch %(echo %{ipipe_patchdir}/ipipe-core-%{LKAver}-*)

# Define the Xenomai version
%define xenomai_version %(rpm -q --qf='%{version}' xenomai-devel)

# Define the buildid, if required.
%define buildid .xenomai

# Temporarily disable parts of build for testing
%define _without_std 1
%define _without_nonpae 1
%define _without_doc 1
%define _without_firmware 1
%define _without_perf 1

# The following build options are enabled by default.
# Use either --without <option> on your rpmbuild command line
# or force the values to 0, here, to disable them.

# PAE kernel
%define with_std          %{?_without_std:          0} %{?!_without_std:          1}
# NONPAE kernel
%define with_nonpae       %{?_without_nonpae:       0} %{?!_without_nonpae:       1}
# Xenomai kernel
%define with_xeno         %{?_without_xeno:         0} %{?!_without_xeno:         1}
# kernel-doc
%define with_doc          %{?_without_doc:          0} %{?!_without_doc:          1}
# kernel-headers
%define with_headers      %{?_without_headers:      0} %{?!_without_headers:      1}
# kernel-firmware
%define with_firmware     %{?_without_firmware:     0} %{?!_without_firmware:     1}
# perf subpackage
%define with_perf         %{?_without_perf:         0} %{?!_without_perf:         1}
# vdso directories installed
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 1}
# use dracut instead of mkinitrd
%define with_dracut       %{?_without_dracut:       0} %{?!_without_dracut:       1}

# Build only the kernel-doc & kernel-firmware packages.
%ifarch noarch
%define with_std 0
%define with_nonpae 0
%define with_headers 0
%define with_perf 0
%define with_vdso_install 0
%define with_xeno 0
%endif

# Build only the 32-bit kernel-headers package.
%ifarch i386
%define with_std 0
%define with_nonpae 0
%define with_doc 0
%define with_firmware 0
%define with_perf 0
%define with_vdso_install 0
%endif

# Build only the 32-bit kernel packages.
%ifarch i686
%define with_doc 0
%define with_headers 0
%define with_firmware 0
%endif

# Build only the 64-bit kernel-headers & kernel packages.
%ifarch x86_64
%define with_nonpae 0
%define with_doc 0
%define with_firmware 0
%endif

# Define the asmarch.
%define asmarch x86

# Define the correct buildarch.
%define buildarch x86_64
%ifarch i386 i686
%define buildarch i386
%endif

# Define the vdso_arches.
%if %{with_vdso_install}
%define vdso_arches i686 x86_64
%endif

# Determine the sublevel number and set pkg_version.
%define sublevel %(echo %{LKAver} | %{__awk} -F\. '{ print $3 }')
%if "%{sublevel}" == ""
%define pkg_version %{LKAver}.0
%else
%define pkg_version %{LKAver}
%endif

# Set pkg_release.
%define pkg_release 1%{?buildid}%{?dist}

#
# Three sets of minimum package version requirements in the form of Conflicts.
#

#
# First the general kernel required versions, as per Documentation/Changes.
#
%define kernel_dot_org_conflicts  ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.0.7-12, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2

#
# Then a series of requirements that are distribution specific, either because
# the older versions have problems with the newer kernel or lack certain things
# that make integration in the distro harder than needed.
#
%define package_conflicts initscripts < 7.23, udev < 145-11, iptables < 1.3.2-1, ipw2200-firmware < 2.4, iwl4965-firmware < 228.57.2, selinux-policy-targeted < 1.25.3-14, squashfs-tools < 4.0, wireless-tools < 29-3

#
# We moved the drm include files into kernel-headers, make sure there's
# a recent enough libdrm-devel on the system that doesn't have those.
#
%define kernel_headers_conflicts libdrm-devel < 2.4.0-0.15

#
# Packages that need to be installed before the kernel because the %post scripts make use of them.
#
%define kernel_prereq fileutils, module-init-tools, initscripts >= 8.11.1-1, grubby >= 7.0.4-1
%if %{with_dracut}
%define initrd_prereq dracut-kernel >= 002-18.git413bcf78
%else
%define initrd_prereq mkinitrd >= 6.0.61-1
%endif

# This takes the 'flavor' argument
%define kernel_reqprovconf \
Provides: kernel = %{version}-%{release}\
Provides: kernel%{?1:-%{1}} = %{version}-%{release}\
Provides: kernel-%{_target_cpu} = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel%{?1:-%{1}}-%{_target_cpu} = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-uname-r = %{version}-%{release}.%{_target_cpu}\
Provides: kernel%{?1:-%{1}}-uname-r = %{version}-%{release}.%{_target_cpu}\
Provides: kernel-drm = 4.3.0\
Provides: kernel-drm-nouveau = 16\
Provides: kernel-modeset = 1\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
Requires(post): /sbin/new-kernel-pkg\
Requires(preun): /sbin/new-kernel-pkg\
%{expand:%{?-r:Requires: %{-r*}}}\
Conflicts: %{kernel_dot_org_conflicts}\
Conflicts: %{package_conflicts}\
Conflicts: %{kernel_headers_conflicts}\
# We can't let RPM do the dependencies automatically because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel proper to function.\
AutoReq: no\
AutoProv: yes

Name: kernel
Summary: The Linux kernel
Group: System Environment/Kernel
License: GPLv2
URL: http://www.kernel.org/
Version: %{pkg_version}
Release: %{pkg_release}
ExclusiveArch: noarch i386 i686 x86_64
ExclusiveOS: Linux

%kernel_reqprovconf

#
# List the packages used during the kernel build.
#
BuildRequires: module-init-tools, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildRequires: bzip2, findutils, gzip, m4, perl, make >= 3.78, diffutils, gawk
BuildRequires: gcc >= 3.4.2, binutils >= 2.12, redhat-rpm-config
BuildRequires: net-tools, patchutils, rpm-build >= 4.8.0-7
BuildRequires: xmlto, asciidoc
%if %{with_perf}
BuildRequires: elfutils-libelf-devel zlib-devel binutils-devel newt-devel
BuildRequires: python-devel perl(ExtUtils::Embed) gtk2-devel bison 
%endif
BuildRequires: python
BuildRequires: xenomai-devel

BuildConflicts: rhbuildsys(DiskFree) < 7Gb

# Sources.
Source0: ftp://ftp.kernel.org/pub/linux/kernel/v3.x/linux-%{LKAver}.tar.bz2
Source1: config-i686
Source2: config-i686-NONPAE
Source3: config-x86_64
Source4: config-xenomai-i686
Source5: config-xenomai-x86_64
Source6: kconfigtool.py

# Patches
#
# (none right now)

%description
This package provides the Linux kernel (vmlinuz), the core of any
Linux-based operating system. The kernel handles the basic functions
of the OS: memory allocation, process allocation, device I/O, etc.

#
# This macro creates a kernel-<subpackage>-devel package.
#	%%kernel_devel_package <subpackage> <pretty-name>
#
%define kernel_devel_package() \
%package %{?1:%{1}-}devel\
Summary: Development package for building kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-devel = %{version}-%{release}\
Provides: kernel%{?1:-%{1}}-devel-%{_target_cpu} = %{version}-%{release}\
Provides: kernel%{?1:-%{1}}-devel-uname-r = %{version}-%{release}.%{_target_cpu}\
AutoReqProv: no\
Requires(pre): /usr/bin/find\
%description %{?1:%{1}-}devel\
This package provides kernel headers and makefiles sufficient to build modules\
against the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage> and its -devel too.
#	%%define variant_summary The Linux kernel compiled for <configuration>
#	%%kernel_variant_package [-n <pretty-name>] <subpackage>
#
%define kernel_variant_package(n:r:) \
%package %1\
Summary: %{variant_summary}\
Group: System Environment/Kernel\
%kernel_reqprovconf\
%{expand:%%kernel_devel_package %1 %{!?-n:%1}%{?-n:%{-n*}}}\
%{nil}


# First the auxiliary packages of the main kernel package.
%kernel_devel_package



%if %{with_nonpae}
%define variant_summary The Linux kernel compiled without PAE support, 32-bit
%kernel_variant_package -n NONPAE nonpae
%description nonpae

32-bit kernel with support for CPUs without (PAE), which can only
address up to 4GB of memory.
%endif



%if %{with_xeno}
%define xeno_requires xenomai == %{xenomai_version}
%define variant_summary The Linux kernel with Xenomai real time system support
%kernel_variant_package -n Xenomai -r %{xeno_requires} xenomai
%description xenomai

This kernel is patched for the Xenomai real-time system.


%if %{with_nonpae}
%define variant_summary The Linux kernel with Xenomai real time system support, non-PAE
%kernel_variant_package -n Xenomai-NONPAE -r %{xeno_requires} xenomai_nonpae

%description xenomai_nonpae

This kernel is patched for the Xenomai real-time system.

32-bit kernel with support for CPUs without (PAE), which can only
address up to 4GB of memory.
%endif # with_nonpae
%endif # with_xeno



%if %{with_doc}
%package doc
Summary: Various bits of documentation found in the kernel sources.
Group: Documentation
Provides: kernel-doc = %{version}-%{release}
%description doc
This package provides documentation files from the kernel sources.
Various bits of information about the Linux kernel and the device
drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to the kernel modules at load time.
%endif

%if %{with_headers}
%package headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Obsoletes: glibc-kernheaders
Provides: glibc-kernheaders = 3.0-46
Provides: kernel-headers = %{version}-%{release}
Conflicts: kernel-headers < %{version}-%{release}
%description headers
This package provides the C header files that specify the interface
between the Linux kernel and userspace libraries & programs. The
header files define structures and constants that are needed when
building most standard programs. They are also required when
rebuilding the glibc package.
%endif

%if %{with_firmware}
%package firmware
Summary: Firmware files used by the Linux kernel
Group: Development/System
License: GPL+ and GPLv2+ and MIT and Redistributable, no modification permitted
Provides: kernel-firmware = %{version}-%{release}
Conflicts: kernel-firmware < %{version}-%{release}
%description firmware
This package provides the firmware files required for some devices to operate.
%endif

%if %{with_perf}
%package -n perf
Summary: Performance monitoring for the Linux kernel
Group: Development/System
License: GPLv2
Provides: perl(Perf::Trace::Context) = 0.01
Provides: perl(Perf::Trace::Core) = 0.01
Provides: perl(Perf::Trace::Util) = 0.01
%description -n perf
This package provides the perf tool and the supporting documentation.
%endif

# Disable the building of the debug package(s).
%define debug_package %{nil}

%prep
%setup -q -n %{name}-%{version} -c
%{__mv} linux-%{LKAver} linux-%{version}-%{release}.%{_target_cpu}
pushd linux-%{version}-%{release}.%{_target_cpu} > /dev/null

# copy raw configs to build directory
mkdir configs
cp $RPM_SOURCE_DIR/config-* configs

# apply RPM patches
# (none right now)

# apply Xenomai patches
ARCH=%{_target_cpu}
# during doc builds, pick an arbitrary arch
test %{_target_cpu} = noarch && ARCH=i686

/usr/src/xenomai/scripts/prepare-kernel.sh --linux=`pwd` \
    --ipipe=%{ipipe_patch} --arch=$ARCH

popd > /dev/null

%build
BuildKernel() {
    %{__make} -s mrproper

    # build flavour config files
    Dash_Flavour=""
    pushd configs
    %{__cp} config-%{_target_cpu} \
        ../config-%{_target_cpu}.intermediate
    for f in $*; do
	%{__python} %{SOURCE6} -m \
	  config-${f}-%{_target_cpu} \
	  ../config${Dash_Flavour}-%{_target_cpu}.intermediate > \
	  ../config${Dash_Flavour}-${f}-%{_target_cpu}.intermediate
        Dash_Flavour="${Dash_Flavour}-${f}"
    done
    popd
    Flavour=${Dash_Flavour#-}

    # Select the correct flavour configuration file.
    %{__cp} config${Dash_Flavour}-%{_target_cpu}.intermediate \
	.config

    %define KVRFA %{version}-%{release}${Flavour:+.$Flavour}.%{_target_cpu}

    # Correctly set the EXTRAVERSION string in the main Makefile.
    EXTRAVERSION=-%{release}${Dash_Flavour//-/.}.%{_target_cpu}
    %{__sed} -i "/^EXTRAVERSION/ s/=.*/= $EXTRAVERSION/" Makefile

    %{__make} -s CONFIG_DEBUG_SECTION_MISMATCH=y ARCH=%{buildarch} V=1 \
	%{?_smp_mflags} bzImage
    %{__make} -s CONFIG_DEBUG_SECTION_MISMATCH=y ARCH=%{buildarch} V=1 \
	%{?_smp_mflags} modules

    # Install the results into the RPM_BUILD_ROOT directory.
    %{__mkdir_p} $RPM_BUILD_ROOT/boot
    %{__install} -m 644 .config $RPM_BUILD_ROOT/boot/config-%{KVRFA}
    %{__install} -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-%{KVRFA}

%if %{with_dracut}
    # We estimate the size of the initramfs because rpm needs to take
    # this size into consideration when performing disk space
    # calculations.  (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-%{KVRFA}.img bs=1M \
	count=20
%else
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initrd-%{KVRFA}.img bs=1M count=5
%endif

    %{__cp} arch/x86/boot/bzImage $RPM_BUILD_ROOT/boot/vmlinuz-%{KVRFA}
    %{__chmod} 755 $RPM_BUILD_ROOT/boot/vmlinuz-%{KVRFA}

    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}
    # Override $(mod-fw) because we don't want it to install any firmware
    # We'll do that ourselves with 'make firmware_install'
    %{__make} -s ARCH=%{buildarch} INSTALL_MOD_PATH=$RPM_BUILD_ROOT \
	modules_install KERNELRELEASE=%{KVRFA} mod-fw=

%ifarch %{vdso_arches}
    %{__make} -s ARCH=%{buildarch} INSTALL_MOD_PATH=$RPM_BUILD_ROOT \
	vdso_install KERNELRELEASE=%{KVRFA}
    if grep '^CONFIG_XEN=y$' .config > /dev/null; then
      echo > ldconfig-kernel.conf "\
# This directive teaches ldconfig to search in nosegneg subdirectories
# and cache the DSOs there with extra bit 0 set in their hwcap match
# fields.  In Xen guest kernels, the vDSO tells the dynamic linker to
# search in nosegneg subdirectories and to match this extra hwcap bit
# in the ld.so.cache file.
hwcap 1 nosegneg"
    fi
    if [ ! -s ldconfig-kernel.conf ]; then
      echo > ldconfig-kernel.conf "\
# Placeholder file, no vDSO hwcap entries used in this kernel."
    fi
    %{__install} -D -m 444 ldconfig-kernel.conf \
	$RPM_BUILD_ROOT/etc/ld.so.conf.d/kernel-%{KVRFA}.conf
%endif

    # Save the headers/makefiles, etc, for building modules against.
    #
    # This looks scary but the end result is supposed to be:
    #
    # - all arch relevant include/ files
    # - all Makefile & Kconfig files
    # - all script/ files
    #
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/source
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    pushd $RPM_BUILD_ROOT/lib/modules/%{KVRFA} > /dev/null
    %{__ln_s} build source
    popd > /dev/null
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/extra
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/updates
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/weak-updates

    # First copy everything . . .
    %{__cp} --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` \
	$RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    %{__cp} Module.symvers $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    %{__cp} System.map $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    if [ -s Module.markers ]; then
      %{__cp} Module.markers $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    fi

    %{__gzip} -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-%{KVRFA}.gz

    # . . . then drop all but the needed Makefiles & Kconfig files.
    %{__rm} -rf $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Documentation
    %{__rm} -rf $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/scripts
    %{__rm} -rf $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include
    %{__cp} .config $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    %{__cp} -a scripts $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    if [ -d arch/%{buildarch}/scripts ]; then
      %{__cp} -a arch/%{buildarch}/scripts \
	$RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/arch/%{_arch} || :
    fi
    if [ -f arch/%{buildarch}/*lds ]; then
      %{__cp} -a arch/%{buildarch}/*lds \
	$RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/arch/%{_arch}/ || :
    fi
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/scripts/*.o
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/scripts/*/*.o
    if [ -d arch/%{asmarch}/include ]; then
      %{__cp} -a --parents arch/%{asmarch}/include \
	$RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/
    fi
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include
    pushd include > /dev/null
    # copy everything under include except Kbuild
    %{__cp} -a [a-z]* $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include
    popd > /dev/null
    # Make a hard-link from the include/linux/ directory to the
    # include/generated/autoconf.h file.
    /bin/ln \
      $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/generated/autoconf.h \
      $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/linux/
    # Copy .config to include/config/auto.conf so a "make prepare" is unnecessary.
    %{__cp} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/.config \
	$RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/config/auto.conf
    # Now ensure that the Makefile, .config, version.h, autoconf.h and
    # auto.conf files all have matching timestamps so that external
    # modules can be built.
    touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile \
	$RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/.config
    touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile \
	$RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/linux/version.h
    touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile \
	$RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/linux/autoconf.h
    touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile \
	$RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/config/auto.conf

    find $RPM_BUILD_ROOT/lib/modules/%{KVRFA} -name "*.ko" -type f > modnames

    # Mark the modules executable, so that strip-to-file can strip them.
    xargs --no-run-if-empty %{__chmod} u+x < modnames

    # Generate a list of modules for block and networking.
    fgrep /drivers/ modnames | xargs --no-run-if-empty nm -upA | \
	sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
      sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef | \
	LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/modules.$1
    }

    collect_modules_list networking \
        'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register'

    collect_modules_list block \
        'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler'

    collect_modules_list drm \
        'drm_open|drm_init'

    collect_modules_list modesetting \
        'drm_crtc_init'

    # Detect any missing or incorrect license tags.
    %{__rm} -f modinfo

    while read i
    do
        echo -n "${i#$RPM_BUILD_ROOT/lib/modules/%{KVRFA}/} " >> modinfo
        /sbin/modinfo -l $i >> modinfo
    done < modnames

    egrep -v \
	'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' \
	modinfo && exit 1

    %{__rm} -f modinfo modnames

    # Remove all the files that will be auto generated by depmod at
    # the kernel install time.
    for i in alias alias.bin ccwmap dep dep.bin ieee1394map inputmap \
	isapnpmap ofmap pcimap seriomap symbols symbols.bin usbmap
    do
        %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/modules.$i
    done

    # Move the development files out of the /lib/modules/ file system.
    %{__mkdir_p} $RPM_BUILD_ROOT/usr/src/kernels
    %{__mv} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build \
	$RPM_BUILD_ROOT/usr/src/kernels/%{KVRFA}
    %{__ln_s} -f ../../../usr/src/kernels/%{KVRFA} \
	$RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
}

%{__rm} -rf $RPM_BUILD_ROOT

pushd linux-%{version}-%{release}.%{_target_cpu} > /dev/null

%if %{with_std}
BuildKernel
%endif

%if %{with_nonpae}
BuildKernel NONPAE
%endif

%if %{with_xeno}
BuildKernel xenomai
%endif

%if %{with_doc}
# Make the HTML and man pages.
%{__make} -s -j1 htmldocs mandocs 2> /dev/null || false

# Sometimes non-world-readable files sneak into the kernel source tree.
%{__chmod} -R a=rX Documentation
find Documentation -type d | xargs %{__chmod} u+w
%endif

%if %{with_perf}
%global perf_make \
  %{__make} -s %{?_smp_mflags} -C tools/perf V=1 HAVE_CPLUS_DEMANGLE=1 \\\
	NO_DWARF=1 prefix=%{_prefix}

%{perf_make} all
%{perf_make} man || false
%endif

popd > /dev/null

%install
pushd linux-%{version}-%{release}.%{_target_cpu} > /dev/null

%if %{with_doc}
docdir=$RPM_BUILD_ROOT%{_datadir}/doc/%{name}-doc-%{version}
man9dir=$RPM_BUILD_ROOT%{_datadir}/man/man9

# Copy the documentation over.
%{__mkdir_p} $docdir
%{__tar} -f - --exclude=man --exclude='.*' -c Documentation | \
	%{__tar} xf - -C $docdir

# Install the man pages for the kernel API.
%{__mkdir_p} $man9dir
find Documentation/DocBook/man -name '*.9.gz' -print0 \
  | xargs -0 --no-run-if-empty %{__install} -m 444 -t $man9dir
%endif

%if %{with_headers}
# Install the kernel headers.
%{__make} -s ARCH=%{buildarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr \
	headers_install

# Do a headers_check but don't die if it fails.
%{__make} -s ARCH=%{buildarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr \
	headers_check > hdrwarnings.txt || :
if grep -q exist hdrwarnings.txt; then
   sed s:^$RPM_BUILD_ROOT/usr/include/:: hdrwarnings.txt
   # Temporarily cause a build failure if there are header inconsistencies.
   # exit 1
fi

# Remove the unrequired files.
find $RPM_BUILD_ROOT/usr/include \
     \( -name .install -o -name .check -o \
        -name ..install.cmd -o -name ..check.cmd \) | xargs %{__rm} -f

# For now, glibc provides the scsi headers.
%{__rm} -rf $RPM_BUILD_ROOT/usr/include/scsi
%{__rm} -f $RPM_BUILD_ROOT/usr/include/asm*/atomic.h
%{__rm} -f $RPM_BUILD_ROOT/usr/include/asm*/io.h
%{__rm} -f $RPM_BUILD_ROOT/usr/include/asm*/irq.h
%endif

%if %{with_firmware}
# It's important NOT to have a .config file present, as it will just
# confuse the system.
%{__make} -s INSTALL_FW_PATH=$RPM_BUILD_ROOT/lib/firmware firmware_install
%endif

%if %{with_perf}
# perf tool binary and supporting scripts/binaries.
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install

# perf man pages. (Note: implicit rpm magic compresses them later.)
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-man || false
%endif

popd > /dev/null

%clean
%{__rm} -rf $RPM_BUILD_ROOT

# Scripts section.
%define flavour_scripts() \
%posttrans %{?1}\
NEWKERNARGS=""\
(/sbin/grubby --info=`/sbin/grubby --default-kernel`) 2>/dev/null | grep -q \\\
    crashkernel\
if [ $? -ne 0 ]; then\
    NEWKERNARGS="--kernel-args=\"crashkernel=auto\""\
fi\
%if %{with_dracut}\
/sbin/new-kernel-pkg --package kernel%{?1:-%{1}} --mkinitrd --dracut \\\
    --depmod --update %{version}-%{release}%{?1:.%{1}}.%{_target_cpu} \\\
    $NEWKERNARGS || exit $?\
%else\
/sbin/new-kernel-pkg --package kernel%{?1:-%{1}} --mkinitrd \\\
    --depmod --update %{version}-%{release}%{?1:.%{1}}.%{_target_cpu} \\\
    $NEWKERNARGS || exit $?\
%endif\
/sbin/new-kernel-pkg --package kernel%{?1:-%{1}} --rpmposttrans \\\
    %{version}-%{release}%{?1:.%{1}}.%{_target_cpu} || exit $?\
if [ -x /sbin/weak-modules ]; then\
    /sbin/weak-modules --add-kernel \\\
	%{version}-%{release}%{?1:.%{1}}.%{_target_cpu} || exit $?\
fi\
if [ -x /sbin/ldconfig ]\
then\
    /sbin/ldconfig -X || exit $?\
fi\
\
%post %{?1}\
if [ `uname -i` == "i386" ] && [ -f /etc/sysconfig/kernel ]; then\
    /bin/sed -r -i -e \\\
        's/^DEFAULTKERNEL=kernel.*/DEFAULTKERNEL=kernel%{?1:-%{1}}/' \\\
	/etc/sysconfig/kernel || exit $?\
fi\
if test "%{1/nonpae/}" = "%{1}"; then  # not PAE\
  if grep --silent '^hwcap 0 nosegneg$' /etc/ld.so.conf.d/kernel-*.conf \\\
    2> /dev/null; then\
      /bin/sed -i '/^hwcap 0 nosegneg$/ s/0/1/' /etc/ld.so.conf.d/kernel-*.conf\
  fi\
fi\
/sbin/new-kernel-pkg --package kernel%{?1:-%{1}} --install \\\
    %{version}-%{release}%{?1:.%{1}}.%{_target_cpu} || exit $?\
\
%preun %{?1}\
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove \\\
    %{version}-%{release}%{?1:.%{1}}.%{_target_cpu} || exit $?\
if [ -x /sbin/weak-modules ]; then\
    /sbin/weak-modules --remove-kernel \\\
        %{version}-%{release}%{?1:.%{1}}.%{_target_cpu} || exit $?\
fi\
if [ -x /sbin/ldconfig ]\
then\
    /sbin/ldconfig -X || exit $?\
fi\
\
%post %{?1:%{1}-}devel\
if [ -f /etc/sysconfig/kernel ]; then\
    . /etc/sysconfig/kernel || exit $?\
fi\
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]; then\
    pushd /usr/src/kernels/%{version}-%{release}%{?1:.%{1}}.%{_target_cpu} \\\
	> /dev/null\
    /usr/bin/find . -type f | while read f; do\
        hardlink -c /usr/src/kernels/*.fc*.*/$f $f\
    done\
    popd > /dev/null\
fi

%if %{with_std}
%flavour_scripts
%if %{with_nonpae}
%flavour_scripts nonpae
%endif
%endif

# xenomai scripts; this should be in a macro
%if %{with_xeno}
%flavour_scripts xenomai
%if %{with_nonpae}
%flavour_scripts xenomai_nonpae
%endif
%endif

# Files section.
%define flavour_files() \
%files %{?1}\
%defattr(-,root,root)\
/boot/vmlinuz-%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}\
/boot/System.map-%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}\
/boot/symvers-%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}.gz\
/boot/config-%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}\
%dir /lib/modules/%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}\
/lib/modules/%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}/kernel\
/lib/modules/%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}/extra\
/lib/modules/%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}/build\
/lib/modules/%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}/source\
/lib/modules/%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}/updates\
/lib/modules/%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}/weak-updates\
%ifarch %{vdso_arches}\
/lib/modules/%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}/vdso\
/etc/ld.so.conf.d/kernel-%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}.conf\
%endif\
/lib/modules/%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}/modules.*\
%if %{with_dracut}\
%ghost /boot/initramfs-%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}.img\
%else\
%ghost /boot/initrd-%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}.img\
%endif\
\
%files %{?1:%{1}-}devel\
%defattr(-,root,root)\
%dir /usr/src/kernels\
/usr/src/kernels/%{version}-%{release}%{?1:.%{1}}.%{_target_cpu}

%if %{with_std}
%flavour_files
%if %{with_nonpae}
%flavour_files nonpae
%endif
%endif

# xenomai files; this should be in a macro
%if %{with_xeno}
%flavour_files xenomai
%if %{with_nonpae}
%flavour_files xenomai_nonpae
%endif
%endif

%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/%{name}-doc-%{version}/Documentation/*
%dir %{_datadir}/doc/%{name}-doc-%{version}/Documentation
%dir %{_datadir}/doc/%{name}-doc-%{version}
%{_datadir}/man/man9/*
%endif

%if %{with_headers}
%files headers
%defattr(-,root,root)
/usr/include/*
%endif

%if %{with_firmware}
%files firmware
%defattr(-,root,root)
/lib/firmware/*
%doc linux-%{version}-%{release}.%{_target_cpu}/firmware/WHENCE
%endif

%if %{with_perf}
%files -n perf
%defattr(-,root,root)
%{_bindir}/perf
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_mandir}/man[1-8]/*
%endif

%changelog
* Fri Dec  6 2013 John Morris <john@zultron.com> - 3.8.13-1
- update to Linux 3.8.13 for Xenomai 2.6.3 release
- update method of applying the Xenomai patch, changed in this release
- updated kernel config files from fedora kernel git rev c64afb6
- don't specify xenomai-devel release explicitly
- find ipipe patch automatically
- remove fc18 perf patch; accepted upstream

* Tue Sep  3 2013 John Morris <john@zultron.com> - 3.5.7-6
- Rename package from kernel-rt back to kernel
- Set buildid to '.xenomai'

* Tue Mar 19 2013 John Morris <john@zultron.com> - 3.5.7-5
- Fix kernel headers to include ipipe and xenomai directories

* Tue Feb 26 2013 John Morris <john@zultron.com> - 3.5.7-4
- Add patch to fix compile error in perf on fc18; this patch looks to
  be in upstream kernels since 2012-07, so hopefully can be removed
  next release

* Fri Jan 25 2013 John Morris <john@zultron.com> - 3.5.7-3
- Update to 2.6.2.1 stable release and ipipe 3.5.7-x86-3
- Minor config tweaks

* Sat Jan 19 2013 John Morris <john@zultron.com> - 3.5.7-2
- Fix Provides: in flavor-devel packages

* Sun Jan 18 2013 John Morris <john@zultron.com> - 3.5.7-1
- Update to 3.5.7 for testing against Xenomai ipipe-gch.git
  for-core-3.5.7 branch
- Update to xenomai_patch_version 3.5.7-x86-0.120115git42cc05f3
  - patch from ipipe-gch.git:  git diff v3.5.7..for-core-3.5.7
- Rename package to kernel-rt
- Build Xenomai as a flavour, kernel-rt-xenomai
- Disable non-rt build by default
- Allow multiple flavours to BuildKernel, e.g. "NONPAE xenomai"
- Wrap specfile lines to fix 80-char terminals
- Macro functions to set up package, description, scripts, files, etc.

* Fri Jan 11 2013 John Morris <john@zultron.com> - 3.5.3-1.el6
- Back down to 3.5.3 to match I-pipe patch

* Thu Jan 10 2013 John Morris <john@zultron.com> - 3.5.5-2.el6
- Added Xenomai real time system
- Rename package to kernel-xenomai
- BR xenomai-devel, and apply patch
- Separate Xeno kernel configs appended to upstream config during
  build

* Thu Oct 04 2012 Alan Bartlett <ajb@elrepo.org> - 3.5.5-1.el6.elrepo
- Updated to the 3.5.5 version source tarball.

* Sat Sep 15 2012 Alan Bartlett <ajb@elrepo.org> - 3.5.4-1.el6.elrepo
- Updated to the 3.5.4 version source tarball.

* Sun Aug 26 2012 Alan Bartlett <ajb@elrepo.org> - 3.5.3-1.el6.elrepo
- Updated to the 3.5.3 version source tarball.

* Wed Aug 15 2012 Alan Bartlett <ajb@elrepo.org> - 3.5.2-1.el6.elrepo
- Updated to the 3.5.2 version source tarball.

* Thu Aug 09 2012 Alan Bartlett <ajb@elrepo.org> - 3.5.1-1.el6.elrepo
- Updated to the 3.5.1 version source tarball.

* Tue Jul 24 2012 Alan Bartlett <ajb@elrepo.org> - 3.5.0-2.el6.elrepo
- Rebuilt with RTLLIB support enabled. [http://elrepo.org/bugs/view.php?id=289]

* Mon Jul 23 2012 Alan Bartlett <ajb@elrepo.org> - 3.5.0-1.el6.elrepo
- Updated to the 3.5 version source tarball.

* Fri Jul 20 2012 Alan Bartlett <ajb@elrepo.org> - 3.4.6-1.el6.elrepo
- Updated to the 3.4.6 version source tarball.

* Tue Jul 17 2012 Alan Bartlett <ajb@elrepo.org> - 3.4.5-1.el6.elrepo
- Updated to the 3.4.5 version source tarball.

* Fri Jun 22 2012 Alan Bartlett <ajb@elrepo.org> - 3.4.4-1.el6.elrepo
- Updated to the 3.4.4 version source tarball.

* Mon Jun 18 2012 Alan Bartlett <ajb@elrepo.org> - 3.4.3-1.el6.elrepo
- Updated to the 3.4.3 version source tarball.

* Sun Jun 10 2012 Alan Bartlett <ajb@elrepo.org> - 3.4.2-1.el6.elrepo
- Updated to the 3.4.2 version source tarball.

* Mon Jun 04 2012 Alan Bartlett <ajb@elrepo.org> - 3.4.1-1.el6.elrepo
- Updated to the 3.4.1 version source tarball.

* Sat May 26 2012 Alan Bartlett <ajb@elrepo.org> - 3.4.0-1.el6.elrepo
- Updated to the 3.4 version source tarball.
- Added a BR for the bison package.
- Added a BR for the gtk2-devel package. [Akemi Yagi]

* Fri May 25 2012 Alan Bartlett <ajb@elrepo.org> - 3.3.7-2.el6.elrepo
- Rebuilt with CEPH support enabled.

* Thu May 24 2012 Alan Bartlett <ajb@elrepo.org> - 3.3.7-1.el6.elrepo
- Updated to the 3.3.7 version source tarball.

* Sun May 20 2012 Alan Bartlett <ajb@elrepo.org> - 3.3.6-2.el6.elrepo
- Corrected the corrupt configuration files.

* Sun May 13 2012 Alan Bartlett <ajb@elrepo.org> - 3.3.6-1.el6.elrepo
- Updated to the 3.3.6 version source tarball.

* Mon May 07 2012 Alan Bartlett <ajb@elrepo.org> - 3.3.5-1.el6.elrepo
- Updated to the 3.3.5 version source tarball.

* Fri Apr 27 2012 Alan Bartlett <ajb@elrepo.org> - 3.3.4-1.el6.elrepo
- Updated to the 3.3.4 version source tarball.
- Re-enabled the build of the perf packages.

* Mon Apr 23 2012 Alan Bartlett <ajb@elrepo.org> - 3.3.3-1.el6.elrepo
- Updated to the 3.3.3 version source tarball.
- Disabled the build of the perf packages due to an undetermined
- bug in the sources. With the 3.3.2 sources, the perf packages will
- build. With the 3.3.3 sources, the perf packages will not build.

* Fri Apr 13 2012 Alan Bartlett <ajb@elrepo.org> - 3.3.2-1.el6.elrepo
- Updated to the 3.3.2 version source tarball.

* Tue Apr 03 2012 Alan Bartlett <ajb@elrepo.org> - 3.3.1-1.el6.elrepo
- Updated to the 3.3.1 version source tarball.

* Mon Mar 19 2012 Alan Bartlett <ajb@elrepo.org> - 3.3.0-1.el6.elrepo
- Updated to the 3.3 version source tarball.

* Tue Mar 13 2012 Alan Bartlett <ajb@elrepo.org> - 3.2.11-1.el6.elrepo
- Updated to the 3.2.11 version source tarball.

* Thu Mar 01 2012 Alan Bartlett <ajb@elrepo.org> - 3.2.9-1.el6.elrepo
- Updated to the 3.2.9 version source tarball.

* Tue Feb 28 2012 Alan Bartlett <ajb@elrepo.org> - 3.2.8-1.el6.elrepo
- Updated to the 3.2.8 version source tarball.

* Tue Feb 21 2012 Alan Bartlett <ajb@elrepo.org> - 3.2.7-1.el6.elrepo
- Updated to the 3.2.7 version source tarball.

* Tue Feb 14 2012 Alan Bartlett <ajb@elrepo.org> - 3.2.6-1.el6.elrepo
- Updated to the 3.2.6 version source tarball.

* Mon Feb 06 2012 Alan Bartlett <ajb@elrepo.org> - 3.2.5-1.el6.elrepo
- Updated to the 3.2.5 version source tarball.

* Sat Feb 04 2012 Alan Bartlett <ajb@elrepo.org> - 3.2.4-1.el6.elrepo
- Updated to the 3.2.4 version source tarball.

* Fri Feb 03 2012 Alan Bartlett <ajb@elrepo.org> - 3.2.3-1.el6.elrepo
- Updated to the 3.2.3 version source tarball.

* Fri Jan 27 2012 Alan Bartlett <ajb@elrepo.org> - 3.2.2-1.el6.elrepo
- Updated to the 3.2.2 version source tarball.
- Adjustments to %%{pkg_version} and %%{pkg_release}
- Adjustments to Conflicts and Provides [Phil Perry]

* Mon Jan 16 2012 Alan Bartlett <ajb@elrepo.org> - 3.2.1-1.el6.elrepo
- General availability.

* Mon Jan 16 2012 Alan Bartlett <ajb@elrepo.org> - 3.2.1-0.rc2.el6.elrepo
- Release candidate 2 for the version 3.2.1 kernel.
- CONFIG_CRYPTO_MANAGER_DISABLE_TESTS=n [Dag Wieers][Akemi Yagi]
- CONFIG_CRYPTO_FIPS=y [Dag Wieers][Akemi Yagi]

* Fri Jan 13 2012 Alan Bartlett <ajb@elrepo.org> - 3.2.1-0.rc1.el6.elrepo
- Updated to the 3.2.1 version source tarball.
- Release candidate 1 for the version 3.2.1 kernel.
- CONFIG_DRM_VMWGFX=m [David Lee]

* Sun Jan 08 2012 Alan Bartlett <ajb@elrepo.org> - 3.1.8-0.rc1.el6.elrepo
- Updated to the 3.1.8 version source tarball.
- Release candidate 1 for the version 3.1.8 kernel.

* Wed Jan 04 2012 Alan Bartlett <ajb@elrepo.org> - 3.1.7-0.rc1.el6.elrepo
- Updated to the 3.1.7 version source tarball.
- Release candidate 1 for the version 3.1.7 kernel.

* Mon Jan 02 2012 Alan Bartlett <ajb@elrepo.org> - 3.1.6-0.rc1.el6.elrepo
- Updated to the 3.1.6 version source tarball.
- Release candidate 1 for the version 3.1.6 kernel.
