% rebase('search_bot.tpl')
<h2 class="result_title">Results For: "{{word}}"</h2>
% if val is not None:
    <h2 class="result_title">Calcuator Result: {{val}}</h2>
%end
% if (num_pages < 1):
    <h2 class="result_title">Sorry, no search results were found</h2>
% else:
	<h2 class="result_title">Page {{from_url/num_displayed + 1}} of {{num_pages}}</h2>
    <div class="results">
    % for url in urls:
	   <a class="link", href="{{url[0]}}">{{url[1]}}</a><br>
       <p class="link">{{url[0]}}</p>
	% end
	</div>

	<div class="page">
    % for i in range(num_pages):
        % params = "/search?" + query + "&from_url=" + str(num_displayed * i)
        <a class="pages", href="{{params}}">{{i+1}}</a>
    % end
    </div>
</table>

