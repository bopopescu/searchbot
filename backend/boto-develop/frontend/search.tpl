% rebase('search_bot.tpl')
<h2>Search For: "{{phrase}}", Number of words: {{num_words}}</h2>
<table id="results">
	<tr>
		<th>Word</th>
		<th>Count</th
	</tr>
%for key, value in counter.items():
	<tr>
		<td>{{key}}</td>
		<td>{{value}}</td>
	</tr>
%end
</table>

