import * as ngPackage from 'ng-packagr';

ngPackage
  .ngPackagr()
  .forProject('ng-package.json')
  .withTsConfig('tsconfig.build.json')
  .build()
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
