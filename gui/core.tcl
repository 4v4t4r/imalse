#
# Copyright 2005-2012 the Boeing Company.
# See the LICENSE file included in this distribution.
#

#
# Copyright 2004-2008 University of Zagreb, Croatia.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# This work was supported in part by Croatian Ministry of Science
# and Technology through the research contract #IP-2003-143.
#

#****h* imunes/imunes.tcl
# NAME
#    imunes.tcl
# FUNCTION
#    Starts imunes in batch or interactive mode. Include procedures from
#    external files and initializes global variables.
#
#	imunes [-b|--batch] [filename]
#    
#    When starting the program in batch mode the option -b or --batch must 
#    be specified. 
#    
#    When starting the program with defined filename, configuration for 
#    file "filename" is loaded to imunes.
#****

if {[lindex $argv 0] == "-b" || [lindex $argv 0] == "--batch"} {
    set argv [lrange $argv 1 end]
    set execMode batch
} elseif {[lindex $argv 0] == "-c" || [lindex $argv 0] == "--closebatch"} {
    set argv [lrange $argv 1 end]
    set execMode closebatch
} else {
    set execMode interactive
}

# 
# Include procedure definitions from external files. There must be
# some better way to accomplish the same goal, but that's how we do it
# for the moment.
#

#****v* imunes.tcl/LIBDIR
# NAME
#    LIBDIR
# FUNCTION
#    The location of imunes library files. The LIBDIR variable
#    will be automatically set to the proper value by the installation script.
#*****

set LIBDIR ""
set SBINDIR "/usr/local/sbin"
set CONFDIR "."
set CORE_STATE_DIR "."
set CORE_START_DIR ""
set CORE_USER ""
if { [info exists env(LIBDIR)] } {
    set LIBDIR $env(LIBDIR)
}
if { [info exists env(SBINDIR)] } {
    set SBINDIR $env(SBINDIR)
}
if { [info exists env(CONFDIR)] } {
    set CONFDIR $env(CONFDIR)
}
if { [info exists env(CORE_STATE_DIR)] } {
    set CORE_STATE_DIR $env(CORE_STATE_DIR)
}
if { [info exists env(CORE_START_DIR)] } {
    set CORE_START_DIR $env(CORE_START_DIR)
}
if { [info exists env(CORE_USER)] } {
    set CORE_USER $env(CORE_USER)
}

source "$LIBDIR/version.tcl"

source "$LIBDIR/linkcfg.tcl"
source "$LIBDIR/nodecfg.tcl"
source "$LIBDIR/ipv4.tcl"
source "$LIBDIR/ipv6.tcl"
source "$LIBDIR/cfgparse.tcl"
source "$LIBDIR/exec.tcl"
source "$LIBDIR/canvas.tcl"

source "$LIBDIR/editor.tcl"
source "$LIBDIR/annotations.tcl"

source "$LIBDIR/help.tcl"
source "$LIBDIR/filemgmt.tcl"

source "$LIBDIR/ns2imunes.tcl"


source "$LIBDIR/mobility.tcl"
source "$LIBDIR/api.tcl"
source "$LIBDIR/wlan.tcl"
source "$LIBDIR/wlanscript.tcl"
source "$LIBDIR/util.tcl"
source "$LIBDIR/plugins.tcl"
source "$LIBDIR/nodes.tcl"
source "$LIBDIR/traffic.tcl"
source "$LIBDIR/exceptions.tcl"

#
# Global variables are initialized here
#

#****v* imunes.tcl/node_list
# NAME
#    node_list
# FUNCTION
#    Represents the list of all the nodes in the simulation. When starting 
#    the program this list is empty.
#*****

#****v* imunes.tcl/link_list
# NAME
#    link_list
# FUNCTION
#    Represents the list of all the links in the simulation. When starting 
#    the program this list is empty.
#*****

#****v* imunes.tcl/canvas_list
# NAME
#    canvas_list
# FUNCTION
#    Contains the list of all the canvases in the simulation. When starting 
#    the program this list is empty.
#*****

#****v* imunes.tcl/prefs
# NAME
#    prefs
# FUNCTION
#    Contains the list of preferences. When starting a program 
#    this list is empty.
#*****

#****v* imunes.tcl/eid
# NAME
#    eid -- experiment id.
# FUNCTION
#    The id of the current experiment. When starting a program this variable 
#    is set to e0.
#*****

set node_list {}
set link_list {}
set annotation_list {}
set canvas_list {}
set eid e0

#****v* core.tcl/exec_servers
# NAME
#    exec_servers -- array of CORE remote execution servers
# FUNCTION
#*****

#	 IP	    port  monitor_port active ssh username
array set exec_servers {}
loadServersConf ;# populate exec_servers

#****v* imunes.tcl/gui_unix
# NAME
#    gui_unix
# FUNCTION
#    false: IMUNES GUI is on MS Windows, 
#    true: GUI is on FreeBSD / Linux / ...
#    Used in spawnShell to start xterm or command.com with NetCat
#*****

if { $tcl_platform(platform) == "unix" } {
    set gui_unix true
} else {
    set gui_unix false
}

# global vars
set showAPI 0
set mac_byte4 0
set mac_byte5 0
set g_mrulist {}
initDefaultPrefs
loadDotFile
# array of hook functions for supporing new node types from ./addons/ dir
#   0 configDialogHook, 1 configDialogIfcHook, 2 configDialogApplyHook,
#   3 button3nodeHook, 4 deployCfgHook, 5 vimageCleanupHook, 6 buttonHook
array set addon_hook_fns { }

loadPluginsConf
autoConnectPlugins


#
# Initialization should be complete now, so let's start doing something...
#

if {$execMode == "interactive"} {
    # GUI-related files
    source "$LIBDIR/widget.tcl"
    source "$LIBDIR/tooltips.tcl"
    source "$LIBDIR/initgui.tcl"
    source "$LIBDIR/topogen.tcl"
    source "$LIBDIR/graph_partitioning.tcl"
    source "$LIBDIR/gpgui.tcl"
    source "$LIBDIR/debug.tcl"
    # Load all Tcl files from the addons directory
    foreach file [glob -nocomplain -directory "$LIBDIR/addons" *.tcl] {
	if { [file isfile $file ] } { source "$file"; }
    }
    # end Boeing
    setOperMode edit
    fileOpenStartUp 
    # Boeing --start option
    foreach arg $argv {
        if { $arg == "--start -s" || $arg == "--start" } {
	    setOperMode exec; break; 
	}
    }
# Boeing changed elseif to catch batch and else to output error
} elseif {$execMode == "batch"} {
    puts "batch execute $argv"
    set sock [lindex [getEmulPlugin "*"] 2]
    if { $sock == "" || $sock == "-1" || $sock == -1 } { exit.real; }
    if {$argv != ""} {
	set fileId [open $argv r]
	set cfg ""
	foreach entry [read $fileId] {
	    lappend cfg $entry
	}
	close $fileId
	after 100 {
	    loadCfg $cfg
	    deployCfgAPI $sock
	    puts "waiting to enter RUNTIME state..."
	}
	global vwaitdummy
	vwait vwaitdummy
    }
} elseif {$execMode == "closebatch"} {
	global g_session_choice
	set g_session_choice $argv
	puts "Attempting to close session $argv ..."
	global vwaitdummy
	vwait vwaitdummy
} else {
    puts "ERROR: execMode is not set in core.tcl"
}

