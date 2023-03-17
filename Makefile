
clean:
	rm -rf ./build ./dist

build_mac_x86:
	poetry run pyinstaller --workpath ./build/mac/x86 --distpath ./dist/mac/x86 --target-arch x86_64 aws_assume_role/cli/main.py

build_mac_arm:
	poetry run pyinstaller --workpath ./build/mac/arm --distpath ./dist/mac/arm --target-arch arm64 aws_assume_role/cli/main.py

build: clean build_mac_x86 build_mac_arm
