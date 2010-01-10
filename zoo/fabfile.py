from __future__ import with_statement
from fabric.api import *
import datetime

def dev():
    "Select dev environment (on local VM)"
    env.hosts = ['localhost']
    env.user_at_host = 'simon@localhost'
    env.deploy_dir = '/srv/django-apps/dev.wildlifenearyou.com'

def staging():
    "Select staging.wildlifenearyou.com"
    env.hosts = ['wildlifenearyou.com']
    env.user_at_host = 'simon@wildlifenearyou.com'
    env.deploy_dir = '/srv/django-apps/staging.wildlifenearyou.com'

def live():
    "Select www.wildlifenearyou.com"
    env.hosts = ['wildlifenearyou.com']
    env.user_at_host = 'simon@wildlifenearyou.com'
    env.db_name = 'zoo_alpha'
    env.deploy_dir = '/srv/django-apps/wildlifenearyou.com'

def restart():
    require('hosts', provided_by = [dev, staging, live])
    sudo('/etc/init.d/apache2 restart')

def restart_nginx():
    require('hosts', provided_by = [dev, staging, live])
    sudo('/etc/init.d/nginx restart')

def mirror_db():
    "Mirror database to local machine"
    env.now = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
    run('mysqldump -u root %(db_name)s > /tmp/%(db_name)s-%(now)s.sql' % env)
    get(
        '/tmp/%(db_name)s-%(now)s.sql' % env, 
        '/tmp/%(db_name)s-%(now)s.sql' % env
    )
    local('mysql -u root zoo_alpha_dev < /tmp/%(db_name)s-%(now)s.sql' % env)

def svn_export():
    "Export latest code"
    env.deploy_date = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
    env.export_path = '/tmp/fab-svn-export/%s' % env.deploy_date
        
    local('mkdir -p %(export_path)s' % env)
    local('svn export . %(export_path)s/zoo' % env)

def rsync_deploy():
    require('export_path', provided_by = [svn_export])
    require('deploy_dir', provided_by = [dev, staging, live])
    run('mkdir -p %(deploy_dir)s' % env)
    local((
        'rsync -a -i --progress --compress '
        '--link-dest=%(deploy_dir)s/current/ '
        '/tmp/fab-svn-export/%(deploy_date)s/ '
        '%(user_at_host)s:%(deploy_dir)s/%(deploy_date)s/ '
    ) % env)
    env.code_is_deployed = True

def repoint_symlink():
    "Symlink $deploy_dir/current to most recent version"
    require('code_is_deployed', provided_by = [rsync_deploy])
    with settings(warn_only = True):
        run('rm %(deploy_dir)s/previous' % env)
        run('mv %(deploy_dir)s/current %(deploy_dir)s/previous' % env)
    run('ln -s %(deploy_dir)s/%(deploy_date)s %(deploy_dir)s/current' % env)
    env.symlink_is_repointed = True

def rollback():
    "Swap current and previous symlinks"
    require('hosts', provided_by = [dev, staging, live])
    require('deploy_dir', provided_by = [dev, staging, live])
    run('mv %(deploy_dir)s/current %(deploy_dir)s/_previous' % env)
    run('mv %(deploy_dir)s/previous %(deploy_dir)s/current' % env)
    run('mv %(deploy_dir)s/_previous %(deploy_dir)s/previous' % env)

def ensure_dependencies():
    "Ensure venv exists and has correct packages installed in it"
    require('hosts', provided_by = [dev, staging, live])
    require('deploy_dir', provided_by = [dev, staging, live])
    require('code_is_deployed', provided_by = [rsync_deploy])
    run((
        'pip install -E  %(deploy_dir)s/venv --enable-site-packages --quiet '
        '-r  %(deploy_dir)s/%(deploy_date)s/zoo/requirements.txt'
    ) % env)

def ensure_dependencies_ignore_installed():
    "Run this if you need to force a full venv refresh"
    require('hosts', provided_by = [dev, staging, live])
    require('deploy_dir', provided_by = [dev, staging, live])    
    run((
        'pip install -E  %(deploy_dir)s/venv --enable-site-packages ' 
        '-r  %(deploy_dir)s/current/zoo/requirements.txt --ignore-installed'
    ) % env)

def deploy():
    "svn_export rsync_deploy repoint_symlink "
    "ensure_dependencies #run_migrations restart_apache"
    require('deploy_dir')
    svn_export()
    rsync_deploy()
    repoint_symlink()
    ensure_dependencies()

#def make_tarball():
#    "Create tarball of latest code"
#    require('export_path', provided_by = [svn_export])
#    local(
#        'cd /tmp/fab-svn-export && ' + 
#        'tar -zcf %(deploy_date)s.tar.gz %(deploy_date)s' % env
#    )
#    local('rm -rf %(export_path)s' % env)
#
#def upload():
#    "Upload tarball of latest code"
#    require('export_path', provided_by = [make_tarball])
#    require('hosts', provided_by = [dev, staging, live])
#    require('deploy_dir', provided_by = [dev, staging, live])
#    run('mkdir -p %(deploy_dir)s' % env)
#    put('%(export_path)s.tar.gz' % env, env.deploy_dir)
#    env.tarball_is_uploaded = True
#
#def untar_on_server():
#    "Untar tarball of latest code"
#    require('tarball_is_uploaded', provided_by = [upload])
#    run('cd %(deploy_dir)s && tar -xzf %(deploy_date)s.tar.gz' % env)
#    env.tarball_is_untarred = True
