import * as md from 'discord-markdown';
import Handlebars from "handlebars";

import './style.css'
import template from './template.hbs?raw'

const params = new URLSearchParams(window.location.search)
const msgUrl = params.get('msg')


const completeEventName = 'completelyFinished'
// @ts-ignore
window.completeEventName = completeEventName
document.addEventListener(completeEventName, () => console.log("DONE!"))


fetch(msgUrl ? `${msgUrl}` : `does-not-exist`)
  .then(async r => {
    console.log(r.status)
    if (r.status == 200) return await r.json()
    else throw Error(`${r.status} - ${msgUrl} - ${await r.text()}`)
  })
  .then(async data => {
    const msg = data

    if (msg.text)
      msg.formatted_text = md.toHTML(msg.text)

    if (msg.embeds)
      for (const embed of msg.embeds) {
        if (embed.title)
          embed.formatted_title = md.toHTML(embed.title)
        if (embed.description)
          embed.formatted_description = md.toHTML(embed.description)
      }

    console.log(data);
    document.querySelector<HTMLDivElement>('#app')!.innerHTML = render({ msg })


    await Promise.all(
      [...document.querySelectorAll('img')]
        .map(img => new Promise((res, rej) => {
          img.onload = res
          img.onerror = rej
        }))
    )

    await new Promise(requestAnimationFrame)

    // @ts-ignore
    window[completeEventName] = true
    document.dispatchEvent(new CustomEvent(completeEventName, { bubbles: true }))
  })
  .catch((err) => {
    console.error(err)
    document.querySelector<HTMLDivElement>('#app')!.innerHTML = `<div style="color:red;">${err}</div>`

    // @ts-ignore
    window[completeEventName] = true
    document.dispatchEvent(new CustomEvent(completeEventName, { bubbles: true }))
  })

const render = Handlebars.compile(template);
