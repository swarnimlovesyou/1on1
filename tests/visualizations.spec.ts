import {test,expect} from '@playwright/test';
import type {Lesson,Trace} from '../src/types';
import {readFileSync} from 'node:fs';
const content=JSON.parse(readFileSync(new URL('../backend/src/main/resources/content.json',import.meta.url),'utf8'));

const capture=new Set(['complexity','hashing','prefix-sums','variable-window','intervals','matrices','linked-list','stack','recursion','avl','heap','tree-traversal','merge-sort','memoization','trie','dijkstra','max-flow','set-cover','bloom-filter']);
for(const lesson of content.lessons as unknown as Lesson[])test(`${lesson.id}: meaningful model, exact seeking and keyboard control`,async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 const response=page.waitForResponse(r=>r.url().endsWith('/api/v1/experiments')&&r.request().method()==='POST');
 await page.goto('/learn/'+lesson.id);
 const trace=await(await response).json() as Trace;
 expect(trace.revision).toBe(3);expect(trace.steps.length).toBeGreaterThan(1);
 await expect(page.locator('.lab-model, .board').first()).toBeVisible();
 const middle=Math.floor(trace.steps.length/2);
 await page.getByRole('slider',{name:'Execution step'}).fill(String(middle));
 await expect(page.locator('.step-explanation p')).toHaveText(trace.steps[middle].text);
 await page.getByRole('slider',{name:'Execution step'}).fill(String(trace.steps.length-1));
 await expect(page.locator('.step-explanation p')).toHaveText(trace.result.text);
 await page.getByRole('slider',{name:'Execution step'}).fill('0');
 await page.locator('.experiment').focus();await page.keyboard.press('ArrowRight');
 await expect(page.getByRole('slider',{name:'Execution step'})).toHaveValue('1');
 if(capture.has(lesson.experiment!.algorithm)){
   await page.getByRole('slider',{name:'Execution step'}).fill(String(middle));
   await page.locator('#experiment').scrollIntoViewIfNeeded();
   for(const width of [1440,390]){
     await page.setViewportSize({width,height:1050});
     await page.locator('.experiment').screenshot({path:`.impeccable/review/lab-${lesson.experiment!.algorithm}-${width}.png`});
     expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
   }
 }
 expect(errors).toEqual([]);
});

test('presets, invalid input recovery and reduced motion preserve authoritative state',async({page})=>{
 await page.emulateMedia({reducedMotion:'reduce'});
 await page.goto('/learn/lesson-matrices');
 await expect(page.getByRole('button',{name:'Next step'})).toBeEnabled();
 await page.getByRole('combobox',{name:'Example input'}).selectOption({label:'Single row'});
 await expect(page.getByLabel('Columns',{exact:true})).toHaveValue('4');
 await page.getByLabel('Columns',{exact:true}).fill('3');
 await page.getByRole('button',{name:'Update experiment'}).click();
 await expect(page.locator('.error-state')).toBeVisible();
 await expect(page.getByText('The previous successful execution stays visible',{exact:false})).toBeVisible();
 await page.getByLabel('Columns',{exact:true}).fill('4');
 await page.getByRole('button',{name:'Update experiment'}).click();
 await expect(page.locator('.error-state')).toHaveCount(0);
 await page.getByRole('slider',{name:'Execution step'}).fill('4');
 await expect(page.locator('.step-explanation')).toContainText('Copy');
 await page.goto('/learn/lesson-bloom-filter');
 await expect(page.getByRole('button',{name:'Next step'})).toBeEnabled();
 await page.getByRole('combobox',{name:'Example input'}).selectOption({label:'An actual false positive'});
 const slider=page.getByRole('slider',{name:'Execution step'});const max=await slider.getAttribute('max');await slider.fill(max!);
 await expect(page.locator('.lab-equation')).toContainText('false positive');
});
