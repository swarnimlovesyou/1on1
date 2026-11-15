import {test,expect} from '@playwright/test';
test('dark mode and intermediate widths keep the notebook usable',async({page})=>{
 await page.addInitScript(()=>localStorage.setItem('1on1-theme','dark'));
 for(const width of [1440,1024,768,390]){
   await page.setViewportSize({width,height:1000});await page.goto('/learn/lesson-sliding-window');await expect(page.getByRole('heading',{name:'A little less work, every time'})).toBeVisible();await expect(page.getByRole('button',{name:'Next step'})).toBeEnabled();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
   if(width===1440||width===390)await page.screenshot({path:'.impeccable/review/'+(width===1440?'desktop':'mobile')+'-dark.png',fullPage:true});
 }
});
