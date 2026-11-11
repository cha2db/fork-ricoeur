/* Shared fixed navigation across the 3 read-only laboratory interfaces.
   No CDN, no network IO, no cookies or tracking. */
(() => {
  "use strict";
  const items = [
    ["▦", "Painel", "/"],
    ["⌕", "Conversas / busca", "/chats"],
    ["◎", "Grafo", "/#graph"],
    ["▥", "Linha do tempo", "/knowledge"],
    ["☷", "Nuvem de termos", "/#tags"],
    ["◇", "Conceitos", "/#concepts"],
    ["⌘", "Terminal / API", "/#terminal"],
    ["◉", "Pesquisa", "/#research"],
    ["©", "Créditos", "/#credits"]
  ];
  const css = `
  :root { --uxnav-width: 228px; }
  body { padding-left: var(--uxnav-width) !important; }
  #ux-global-nav { position:fixed; top:0; bottom:0; left:0; width:var(--uxnav-width);
    z-index:200; overflow-y:auto; overscroll-behavior:contain; padding:20px 12px;
    background:#0a1729; border-right:1px solid #32445e;
    box-shadow:3px 0 18px #0002; font:14px/1.4 system-ui,sans-serif; }
  #ux-global-nav .ux-brand { color:#f5f9ff; font-size:17px; font-weight:750;
    padding:10px 12px 19px; border-bottom:1px solid #32445e; margin-bottom:16px; }
  #ux-global-nav a { display:flex; gap:12px; align-items:center; padding:10px 11px; margin:3px 0;
    border:1px solid transparent; border-radius:10px; text-decoration:none; color:#bfd0e6;
    white-space:nowrap; }
  #ux-global-nav a:hover, #ux-global-nav a:focus-visible, #ux-global-nav a[aria-current=page] {
    background:#1e3452; color:#fff; border-color:#43648d; outline:none; }
  #ux-global-nav .ux-footer { margin:20px 8px; padding-top:14px; border-top:1px solid #32445e;
    color:#8fa7c1; font-size:11px; }
  :where(section[id]) {scroll-margin-top:30px}
  @media(max-width:800px) {
    :root { --uxnav-width: 0px; }
    body {padding-left:0 !important}
    #ux-global-nav {position:sticky; top:0; bottom:auto; left:auto; width:100%;
      display:flex; align-items:center; overflow-x:auto; overflow-y:hidden; padding:5px;
      border-right:0; border-bottom:1px solid #32445e; white-space:nowrap; }
    #ux-global-nav .ux-brand {white-space:nowrap; border:0; padding:6px 10px;
      margin:0; font-size:13px;}
    #ux-global-nav .ux-links {display:flex; gap:2px;}
    #ux-global-nav a {padding:8px 10px; font-size:12px; margin:0}
    #ux-global-nav .ux-footer {display:none}
    :where(section[id]){scroll-margin-top:80px}
  }`;
  const style = document.createElement("style"); style.textContent=css;
  document.head.append(style);
  const nav = document.createElement("nav");
  nav.id="ux-global-nav";
  nav.setAttribute("aria-label","Navegação principal fixa");
  const brand = document.createElement("div");
  brand.className="ux-brand";brand.textContent="Cha2db · UX";
  nav.append(brand);
  const links=document.createElement("div");links.className="ux-links";
  const path=location.pathname;
  items.forEach(([glyph,label,href])=>{
    const a=document.createElement("a");a.href=href;a.textContent=glyph+"  "+label;
    if(href===(path==="/" ? "/" : path))a.setAttribute("aria-current","page");
    links.append(a);
  });
  nav.append(links);
  const footer=document.createElement("div");footer.className="ux-footer";
  footer.textContent="Pesquisa aberta · núcleo Ricoeur · dados locais";
  nav.append(footer);
  document.body.prepend(nav);
})();
