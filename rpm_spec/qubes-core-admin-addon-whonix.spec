%{!?version: %define version %(cat version)}

Name:		qubes-core-admin-addon-whonix
Version:	%{version}
Release:	1%{?dist}
Summary:	qubes-core-admin extension for handling Whonix related settings

Group:		Qubes
License:	GPLv2+
URL:		https://www.qubes-os.org

BuildArch:	noarch
BuildRequires:	python3-devel

%if 0%{?qubes_builder}
%define _builddir %(pwd)
%endif

%description
qubes-core-admin extension for handling Whonix related settings

%prep
%if !0%{?qubes_builder}
%setup -q
%endif

%build
make %{?_smp_mflags}


%install
%make_install


%files
%doc README.md
%{python3_sitelib}/qubeswhonix-*.egg-info
%{python3_sitelib}/qubeswhonix

%changelog

