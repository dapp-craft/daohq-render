import { defineConfig } from 'vite'
import dynamicPublicDirectory from "vite-multiple-assets";
import fs from 'fs'
// same level as project root

export default defineConfig(({ command }) => {
    if (command === 'serve') {
        return {
            // dev specific config
            build: {
                minify: false,
            },
            plugins: [
                dynamicPublicDirectory(([] as string[])
                    .concat(fs.existsSync('public-dev') ? ['public-dev'] : [])
                    .concat(fs.existsSync('public') ? ['public'] : [])
                )
            ]
        }
    } else {
        // command === 'build'
        return {
            // build specific config
            base: '',
            build: {
                minify: false,
                outDir: '../../static/discord',
                emptyOutDir: true,
            },
        }
    }
})