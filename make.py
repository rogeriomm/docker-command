#!python3

# https://newbedev.com/6-ways-to-call-external-command-in-python

import os
import sys
import docker
from git import Repo
from colorama import Fore, Style
import getpass

try:
    dc = docker.from_env()
except:
    pass

tls_config = docker.tls.TLSConfig(
        ca_cert=dc.api.verify,
        client_cert=dc.api.cert,
        verify=True)

# https://www.programcreek.com/python/?code=picoCTF%2FpicoCTF%2FpicoCTF-master%2FpicoCTF-shell%2Fhacksport%2Fdocker.py: Search "tls_config"
cli = docker.APIClient(base_url=dc.api.base_url, tls=tls_config)
username = getpass.getuser()
github_username = "rogeriomm"


class DockerBuildComponent:
    """ Docker build component """

    def __init__(self, name: str, version: str = '', parm={}, prefix='', depends=[]):
        self.name = name
        self.prefix = prefix
        self.version = version
        self.parm = parm
        self.username = username
        self.__repo = Repo('.')
        self.__dir = os.getcwd()
        self.__branch = self.__repo.active_branch.name

    def show(self):
        # print(f"Current directory: {self.__dir}")
        # print(f"Path: {self.__path}")
        # print(f"Repository: {self.__repo}")
        # print(f"Current branch: {self.__branch}")
        # print(f"Is dirty? {self.__repo.is_dirty()}")
        # print(f"Parameters: {self.parm}")
        print(f"   name: \"{self.name}\", prefix: \"{self.prefix}\", version: \"{self.version}\", parm: {self.parm} ")

    def get_docker_name(self) -> str:
        tag = ""
        if self.prefix == '' and self.version == '':
            tag = f"{self.username}/{self.name}:{self.__branch}"
        elif self.prefix == '' and self.version != '':
            tag = f"{self.username}/{self.name}-{self.version}:{self.__branch}"
        elif self.prefix != '' and self.version != '':
            tag = f"{self.username}/{self.prefix}-{self.name}-{self.version}:{self.__branch}"
        elif self.prefix != '' and self.version == '':
            tag = f"{self.username}/{self.prefix}-{self.name}:{self.__branch}"
        return tag

    # https://docker-py.readthedocs.io/en/stable/api.html#module-docker.api.build
    def build(self) -> bool:
        args = {"TAG": self.__branch, "USERNAME": self.username}
        args.update(self.parm)

        tag = self.get_docker_name()

        print(f"============ Building {tag} ============ {args}")

        streamer = cli.build(path=f"./{self.name}", tag=tag,
                             nocache=False, rm=False, buildargs=args,
                             forcerm=True,
                             decode=True)
        success = True

        for chunk in streamer:
            if 'stream' in chunk:
                for line in chunk['stream'].splitlines():
                    print(line)
            elif 'status' in chunk:
                print(f"{Fore.GREEN}{chunk}{Style.RESET_ALL}")
            elif 'message' in chunk:
                for line in chunk['message'].splitlines():
                    print(f"{Fore.YELLOW}{line}{Style.RESET_ALL}")
                success = False
            elif 'aux' in chunk:
                pass
            elif 'errorDetail' in chunk:
                print(f"{Fore.YELLOW}{chunk['errorDetail']}{Style.RESET_ALL}")
                success = False
            elif "\n" in chunk:
                print("")
            else:
                print(f"######### Unknown chunk ########## {chunk}")

        return success


class DirComponent:
    """ Directory """

    def __init__(self, name="", dirs=[]):
        self.name = name
        self.dirs = dirs
        self.scanned = False

    def show(self):
        print(f"   name: {self.name}: dirs: {self.dirs}")


def add_mk(pkg: [], name: str):
    global flprj
    flprj.add_pkg(name, pkg)


def dir_mk(d: [], name: str):
    global flprj
    flprj.add_dir(name, d)


class BuildMk:
    """ build.mk file """

    def __init__(self):
        self.__hasPrjFile = False
        self.__pkgs = []
        self.__dirs = []
        self.__dir = os.getcwd()

    def has_prj_file(self) -> bool:
        return self.__hasPrjFile

    def get_repos_name(self):
        return os.path.basename(self.__dir)

    def get_pkgs(self) -> []:
        return self.__pkgs

    def get_dirs(self) -> []:
        return self.__dirs

    def get_prj_dir(self) -> str:
        return self.__dir

    def add_pkg(self, name='', p=[]):
        if name != '' and len(p) > 0:
            self.__pkgs.append(p)

    def add_dir(self, name='', d=[]):
        if name != '' and len(d) > 0:
            self.__dirs.append(DirComponent(name, d))

    def scan(self):
        global flprj
        os.chdir(self.__dir)
        try:
            flprj = self
            self.__pkgs = []
            self.__dirs = []
            with open('build.mk', mode='r', encoding='utf8') as f:
                eval(f.read(),
                     {'__builtins__': None}, {'Docker': DockerBuildComponent, 'Prj': add_mk, 'Dir': dir_mk})
                f.close()
                self.__hasPrjFile = True
        except IOError:
            self.__hasPrjFile = False
        finally:
            flprj = None

    def build(self):
        os.chdir(self.__dir)
        for p in self.__pkgs:
            if type(p) is list:
                for c in p:
                    if not c.build():
                        break  # Build failed
            else:
                break  # Failed

    def show(self):
        print("=====================================================================================")
        print(f"Path: {self.__dir}")
        if self.__hasPrjFile:
            for p in self.__pkgs:
                if type(p) is list:
                    for c in p:
                        c.show()
            if len(self.__dir) > 0:
                for p in self.__dirs:
                    if type(p) is DirComponent:
                        p.show()


flprj: BuildMk


class AllBuildMk:
    """ All projects """

    def __init__(self):
        self.__prjs = []
        self.__dir = os.getcwd()

    def scan(self):
        """ Scan recursively """
        p = BuildMk()
        p.scan()
        self.__prjs.append(p)
        if p.has_prj_file():
            for d in p.get_dirs():
                cur_dir = os.getcwd()  # save current directory
                for i in d.dirs:
                    os.chdir(i)
                    self.scan()
                    os.chdir(cur_dir)

    def show(self):
        for p in self.__prjs:
            if type(p) is BuildMk:
                p.show()

    def build(self):
        for p in self.__prjs:
            if type(p) is BuildMk:
                p.build()
            else:
                break

    def command(self, cd: []) -> bool:
        cur_dir = os.getcwd()

        match cd:
            case ["show"]:
                self.show()
                return True

        try:
            for p in self.__prjs:
                print(f"===> {p.get_repos_name()}")
                os.chdir(p.get_prj_dir())
                match cd:
                    case ["build"]:
                        p.build()

                    case ["add", "origin"]:
                        cmd = f"git remote add origin git@github.com:{github_username}/{p.get_repos_name()}.git"
                        os.system(cmd)

                    case ["remove", "origin"]:
                        cmd = f"git remote remove origin"
                        os.system(cmd)

                    case ["push", "all"]:
                        cmd = f"git push --all origin"
                        os.system(cmd)

                    case ["delete", "repos", "github"]:
                        cmd = f"gh repo-delete {github_username}/{p.get_repos_name()}"
                        os.system(cmd)

                    case ["create", "repos", where]:
                        match where:
                            case "github":
                                cmd = f"gh repo create {github_username}/{p.get_repos_name()} --confirm --public " + \
                                      f"--description \"{p.get_repos_name()}\""
                                os.system(cmd)
                            case "bitbucket":
                                cmd = f""
                                os.system(cmd)

                    case ["ps"]:
                        if os.path.isfile("docker-compose.yml"):
                            cmd = f"export TAG=$(git rev-parse --abbrev-ref HEAD) ; docker-compose -f docker-compose.yml ps"
                            os.system(cmd)

                    case ["start"]:
                        if os.path.isfile("docker-compose.yml"):
                            cmd = f"export TAG=$(git rev-parse --abbrev-ref HEAD) ; docker-compose -f docker-compose.yml up -d"
                            os.system(cmd)

                    case ["stop"]:
                        if os.path.isfile("docker-compose.yml"):
                            cmd = f"export TAG=$(git rev-parse --abbrev-ref HEAD) ; docker-compose -f docker-compose.yml down"
                            os.system(cmd)

                    case ["shell", name]:
                        if os.path.isfile("docker-compose.yml"):
                            cmd = f"export TAG=$(git rev-parse --abbrev-ref HEAD) ; docker-compose -f docker-compose.yml exec {name} /bin/bash"
                            os.system(cmd)
                            return True

                    case _:
                        return False

        finally:
            os.chdir(cur_dir)

        return True


def main():
    p = AllBuildMk()
    p.scan()
    argv = sys.argv[1:]
    if len(argv) == 0:
        return
    if not p.command(argv):
        print("Invalid command")


if __name__ == '__main__':
    main()
