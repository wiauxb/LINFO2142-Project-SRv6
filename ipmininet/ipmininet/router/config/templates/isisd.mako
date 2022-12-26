hostname ${node.name}
password ${node.password}

% if node.isisd.logfile:
log file ${node.isisd.logfile}
% endif

% for section in node.isisd.debug:
debug isis ${section}
% endfor
