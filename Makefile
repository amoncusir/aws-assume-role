
clean:
	rm -rf ./build ./dist

build_mac_x86: clean
	poetry run pyinstaller -n aws-assume-role --workpath ./build/mac/x86 --distpath ./dist/mac/x86 --target-arch x86_64 aws_assume_role/cli/main.py

build_mac_arm: clean
	poetry run pyinstaller -n aws-assume-role --workpath ./build/mac/arm --distpath ./dist/mac/arm --target-arch arm64 aws_assume_role/cli/main.py
