Cu.importGlobalProperties(["TextEncoder", "TextDecoder"]);

function isSafeProfileFilename(filename) {
  return (
    typeof filename === "string" &&
    /^[A-Za-z0-9._-]{1,128}$/.test(filename) &&
    filename.indexOf("..") === -1
  );
}

this.profileDirIO = class extends ExtensionAPI {
  getAPI(_context) {
    return {
      profileDirIO: {
        async writeFile(filename, data) {
          if (!isSafeProfileFilename(filename)) {
            console.error("Rejected profile filename", filename);
            return false;
          }
          const encoder = new TextEncoder();
          const array = encoder.encode(data);
          const path = PathUtils.join(PathUtils.profileDir, filename);
          const tmpPath = PathUtils.join(
            PathUtils.profileDir,
            filename + ".tmp",
          );
          try {
            await IOUtils.write(path, array, { tmpPath });
            console.log(`Wrote to ${path}`);
            return true;
          } catch (e) {
            Cu.reportError(e);
            return false;
          }
        },
        async readFile(filename) {
          if (!isSafeProfileFilename(filename)) {
            console.error("Rejected profile filename", filename);
            return "";
          }
          const decoder = new TextDecoder();
          const path = PathUtils.join(PathUtils.profileDir, filename);
          try {
            const array = await IOUtils.read(path);
            return decoder.decode(array);
          } catch (e) {
            Cu.reportError(e);
            return "";
          }
        },
      },
    };
  }
};
